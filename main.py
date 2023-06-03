import os
from _socket import gaierror
from argparse import ArgumentParser
from client import Client

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--from', type=str, default='<>', dest='sender', help='Отправитель')
    parser.add_argument('-t', '--to', type=str, help='Получатель')
    parser.add_argument('-d', '--directory', type=str, default=os.getcwd(), help='Директория(по умолчанию pwd)')
    parser.add_argument('--subject', type=str, default='Pictures',
                        help='Название письма')
    parser.add_argument('-s', '--server', type=str, default='smtp.mail.ru:25',
                        help='Адрес')
    parser.add_argument('--ssl', action='store_true',
                        help='Использование ssl')
    parser.add_argument('--auth', action='store_true', help='Запрашивать ли авторизацию')
    parser.add_argument('-v', '--verbose', action='store_true', help='Отображение работы')

    args = parser.parse_args()
    try:
        client = Client(args.sender, args.to, args.subject, args.ssl, args.auth, args.verbose, args.directory,
                        args.server)
        client.run()
    except ValueError as e:
        print(e)
    except gaierror:
        print('DNS Error')
    except ConnectionError:
        print('Connection error')
