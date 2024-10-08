def bulls_cows(secret, guess):
    # inputs are both strings, output should be string w/format xAyB x are bulls y are cows
    # length is equal for both secret and guess
    # bulls are the right digit in the right position
    # cows are the right digit but in a wrong position
    bulls = 0
    cows = 0

    for i, c in enumerate(guess):
        if c == secret[i]:
            bulls += 1
            secret = secret[0:i] + 'x' + secret[i+1:]

    for i, c in enumerate(guess):
        if c in secret:
            cows += 1
            secret = secret[0:secret.index(c)] + 'x' + secret[secret.index(c)+1:]

    return f'{bulls}A{cows}B'

# print(bulls_cows('1234', '4231'))
print(bulls_cows('1111', '1000'))
