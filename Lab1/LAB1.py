import random
import warnings
import pandas
from concurrent.futures import ProcessPoolExecutor as Pool

LETTERS_MAS = ['A','B','C','D']

# Генерация файлов и заполнение их данными
def createFiles():
    for i in range(5):
        with open('data' + str(i + 1) + '.csv','w') as f:
            f.write("LETTERS,NUMBERS\n")
            for j in range(random.randint(1,20)):
                f.write(f'{random.choice(LETTERS_MAS)},{round(random.uniform(0,10), 2)}\n')
    return

# Считывание файлов, подсчёт медианы и стандартного отклонения
def parseFile(fileName):
    df = pandas.read_csv(fileName)
    resultMas = {
        "fileName":fileName,
        "median": {},
        "deviation": {}
    }
    for letter in LETTERS_MAS:
        medianValue = df[df['LETTERS'] == letter]['NUMBERS'].median()
        deviationValue = df[df['LETTERS'] == letter]['NUMBERS'].std()
        resultMas["median"][letter] = medianValue
        resultMas["deviation"][letter] = deviationValue
    return resultMas

# Главная функция обработки вскех файлов
def main():
    warnings.filterwarnings('ignore')

    print('Желаете пересоздать файлы:\n1 - ДА\n2 - НЕТ')
    ans = input("ВВЕДИТЕ ОТВЕТ:")

    if ans == '1':
        createFiles()
        flag = True
    elif ans == '2':
        flag = True
    else:
        flag = False
        print('НЕВЕРНЫЙ ОТВЕТ - ВЫХОД')

    if flag == True:

        MEDIAN_MAS = { "A" : [], "B" : [], "C" : [], "D" : [] }

        with Pool(max_workers=5) as workPool:
            results = list(workPool.map(parseFile,[f"data{i+1}.csv" for i in range(5)]))
            for result in results:
                print("-"*20 + "\n" + result["fileName"] + "\n" + "-"*20)
                for letter in LETTERS_MAS:
                    MEDIAN_MAS[letter].append(round(result["median"][letter],2))
                    print(f'{letter:<2} | {round(result["median"][letter],2):<5}  | {round(result["deviation"][letter],2):<5}')

            #Нахождение медианы медиан и стандартного отклонения медиан
            print('-'*20 + '\nРЕЗУЛЬТАТ ПО ВСЕМ ФАЙЛАМ\n' + 20*'-')
            for letter in LETTERS_MAS:
                allMedians = pandas.Series(MEDIAN_MAS[letter]).median()
                allDeviation = pandas.Series(MEDIAN_MAS[letter]).std()
                print(f'{letter:<2} | {round(allMedians,2):<5} | {round(allDeviation,2):<5}')
            print('-'*20)

    return

if __name__ == "__main__":
    main()