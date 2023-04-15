def jainsall(data):  # Function with "data" as parametre. In this case we intend to use a list from text file (the task)
    N = len(liste)  # The amount of elements in the list

    # Decided that it would be easier to define the numerator and the denominator

    numerator = sum(liste)  # Calculating the numerator of the JFI formula by summing the values in the list
    denominator = sum(
        x ** 2 for x in liste)  # Calculating the denominator by summing the squares of the values in the list
    jfi = (numerator ** 2) / (N * denominator)  # Using the formula for JFI, using the variables defined above
    return round(jfi, 4)  # Returning the result with 4 decimals


liste = []  # empty list

with open("tc5") as file:  # Open the file "task3.txt"
    for line in file:
        throughputs = line.split()  # Splitting the lines
        print(throughputs)  # Printing the lines "elements" in the list for overview
        liste.append(float(throughputs[0]))  # Adding the values as elements to the list

print(jainsall(liste))  # Calling the jainsall function with the list of values as parametre