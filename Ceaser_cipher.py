def ceaser_encrypt(text, key):
    result = ""
    for i in range(len(text)):
        char = text[i]
        if "A" <= char <= "Z":
            result = result + chr((ord(char) + key - 65) % 26 + 65)
        elif 97 <= ord(char) <= 122:
            result = result + chr((ord(char) + key - 97) % 26 + 97)
        else:
            result =  result + char
    return result

def ceaser_decrypt_hack(text, k):
    KYTU = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    decryped_msg = []
    for key in range(len(KYTU)):
        result = ""
        for symbol in text:
            if symbol in KYTU:
                num = KYTU.find(symbol)
                num = num - key
                if(num < 0):
                    num = num + len(KYTU)
                result = result + KYTU[num]
            else:
                result = result + symbol
        decryped_msg.append(result)
    return decryped_msg[k]
