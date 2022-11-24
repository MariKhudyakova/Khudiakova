import table_out
import report_out


def main():
    choice = input('Введите вид формирования данных: ')
    if choice == "Вакансии":
        print("Введите данные для печати:")
        table_out.get_table()
    elif choice == "Статистика":
        print("Введите данные для печати:")
        report_out.get_report()
    else:
        print("Неверный ввод, проверьте корректность ввода")


main()
