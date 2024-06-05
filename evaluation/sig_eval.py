import pandas as pd

"""
The Lenstra and Bellcore evaluation code is taken from the Voltpillager paper's demo repository.
"""

fault_str = "Faulted result\nResult = 1\n"

p = 0xEECFAE81B1B9B3C908810B10A1B5600199EB9F44AEF4FDA493B81A9E3D84F632124EF0236E5D1E3B7E28FAE7AA040A2D5B252176459D1F397541BA2A58FB6599
q = 0xC97FB1F027F453F6341233EAAAD1D9353F6C42D08866B1D05A0F2035028B9D869840B41666B42E92EA0DA3B43204B5CFCE3352524D0416A5A441E700AF461503
n = 0xBBF82F090682CE9C2338AC2B9DA871F7368D07EED41043A440D6B6F07454F51FB8DFBAAF035C02AB61EA48CEEB6FCD4876ED520D60E1EC4619719D8A5B8B807FAFB8E0A3DFC737723EE6B4B7D93A2584EE6A649D060953748834B2454598394EE0AAB12D7B61A51F527A9A41F6C1687FE2537298CA2A8F5946F8E5FD091DBDCB
d = 0xA5DAFC5341FAF289C4B988DB30C1CDF83F31251E0668B42784813801579641B29410B3C7998D6BC465745E5C392669D6870DA2C082A939E37FDCB82EC93EDAC97FF3AD5950ACCFBC111C76F1A9529444E56AAF68C56C092CD38DC3BEF5D20A939926ED4F74A13EDDFBE1A1CECC4894AF9428C2B7B8883FE4463A4BC85B1CB3C1
e = 17

dP = 0x54494CA63EBA0337E4E24023FCD69A5AEB07DDDC0183A4D0AC9B54B051F2B13ED9490975EAB77414FF59C1F7692E9A2E202B38FC910A474174ADC93C1F67C981
dQ = 0x471E0290FF0AF0750351B7F878864CA961ADBD3A8A7E991C5C0556A94C3146A7F9803F8F6F8AE342E931FD8AE47A220D1B99A495849807FE39F9245A9836DA3D
invQ = 0xB06C4FDABB6301198D265BDBAE9423B380F271F73453885093077FCD39E2119FC98632154F5883B167A967BF402B4E9E2E0F9656E698EA3666EDFB25798039F7

ct = 0x1253E04DC0A5397BB44A7AB87E9BF2A039A33D1E996FC82A94CCD30074C95DF763722017069E5268DA5D1C0B4F872CF653C11DF82314A67968DFEAE28DEF04BB6D84B1C31D654A1970E5783BD6EB96A024C2CA2F4A90FE9F2EF5C9C140E5BB48DA9536AD8700C84FC9130ADEA74E558D51A74DDF85D8B50DE96838D6063E0955
pt_exp = 0x00EB7A19ACE9E3006350E329504B45E2CA82310B26DCD87D5C68F1EEA8F55267C31B2E8BB4251F84D7E0B2C04626F5AFF93EDCFB25C9C2B3FF8AE10E839A2DDB4CDCFE4FF47728B4A1B7C1362BAAD29AB48D2869D5024121435811591BE392F982FB3E87D095AEB40448DB972F3AC14F7BC275195281CE32D2F1B76D4D353E2D
pt = pow(ct, d, n)


def list_to_int(l):
    r = 0
    for i in range(0, len(l)):
        r <<= 8
        r |= l[len(l) - i - 1]
    return r


def compute_GCD(x, y):
    while (y):
        x, y = y, x % y
    return x


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


def print_factor(x):
    if x == p:
        print("P found")
    elif x == q:
        print("Q found")
    else:
        print("Unknown factor")


def get_faults_from_log():
    from dataframe import create_rounds_blocks
    file = "local_logs/sgx_iterations/subprocess-2024-05-11-13-04-49.log"
    faults = []
    with open(file) as f:
        lines = f.readlines()
    blocks = create_rounds_blocks(lines)
    for block in blocks:
        for round in block:
            i = round.find(fault_str)
            if i != -1:
                hex_str = round[i + len(fault_str):round.find('\n', i + len(fault_str))]
                faults.append(transform_fault_str(hex_str))
    return faults

def transform_fault_str(fault, type):
    fault = fault.strip()
    if type == 'mult':
        sep = " =/= "
        for_s = ' for '
        and_s = ' and '
        i = fault.find(sep)
        if i == -1:
            print("huh fault string does not contain sep")
            return 'No fault'
        mul1 = int(fault[:i])
        j = fault.find(for_s, i)
        mul2 = int(fault[i+len(sep):j])
        k = fault.find(and_s, j)
        int1 = int(fault[j+len(for_s):k])
        int2 = int(fault[k+len(and_s):-1])
        return (mul1, mul2, int1, int2)
    elif type == 'sgx':
        if fault.endswith(','):
            fault = fault[:-1]
        fault = fault.split(', ')
        return [int(i, 16) for i in fault]
    else:
        print("unknown type")
        return 'No fault'

def analyze_faults(faults):
    bellcore_p = []
    lenstra_p = []
    ratios = []
    for fault in faults:
        pt_fault = list_to_int(fault)
        assert pt != pt_fault

        diff = bin(pt ^ pt_fault)
        ones = diff.count('1')
        zeros = diff.count('0') - 1
        ratios.append(ones / (zeros + ones))

        bellcore = compute_GCD((pt - pt_fault) % n, n)
        if bellcore == p:
            bellcore_p.append('p')
        elif bellcore == q:
            bellcore_p.append('q')
        else:
            print(f"Unknown factor: {hex(bellcore)}")
            bellcore_p.append('?')

        lenstra = compute_GCD((pow(pt_fault, e, n) - ct) % n, n)
        if lenstra == p:
            lenstra_p.append('p')
        elif lenstra == q:
            lenstra_p.append('q')
        else:
            print(f"Unknown factor: {hex(lenstra)} for {hex(list_to_int(fault))}")
            lenstra_p.append('?')

    return pd.DataFrame({'Ratios': ratios,
                         'Lenstra': lenstra_p,
                         'Bellcore': bellcore_p})


if __name__ == "__main__":
    from evaluation.faults import *

    # print(get_faults_from_log())

    # for fault in my_first_faults:
    #     pt_fault = list_to_int(fault)

    #     print(f"Correct: {hex(pt)}\n")
    #     print(f"Faulty: {hex(pt_fault)}\n")
    #     assert pt != pt_fault

    #     diff = bin(pt ^ pt_fault)
    #     print(f"Diff: {diff}\nones: {diff.count('1')} | zeros: {diff.count('0')-1}\n")

    #     # Bellcore
    #     print("Factoring with Bellcore: ")
    #     bellcore = compute_GCD((pt - pt_fault) % n, n)
    #     print(hex(bellcore))
    #     print_factor(bellcore)
    #     print()
    #     # Lenstra
    #     print("Factoring with Lenstra:  ")
    #     lenstra = compute_GCD((pow(pt_fault, e, n) - ct) % n, n)
    #     print(hex(lenstra))
    #     print_factor(lenstra)
    #     print()
    #     print("========================
    # ==================\n")
    df = analyze_faults(subprocess20240511130449)

    print(f"Lenstra counts: {df['Lenstra'].value_counts()}")
    print(f"Bellcore counts: {df['Bellcore'].value_counts()}")
