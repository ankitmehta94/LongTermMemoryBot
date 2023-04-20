from generate_response import generate_response


if __name__ == '__main__':
    while True:
        # get user input, save it, vectorize it, etc
        a = input('\n\nUSER: ')
        generate_response(a)
