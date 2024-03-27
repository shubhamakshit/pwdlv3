def log(message):
    with open('log.txt','a') as file:
        file.write(f'{message}')
        file.write('\n')