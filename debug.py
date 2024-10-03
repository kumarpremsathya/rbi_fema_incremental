numberList = [15, 85, 35, 89, 125]
sort_list = []

# Loop until numberList is empty
while numberList:
    # Assume the first element is the maximum
    maxNum = numberList[0]
    
    # Debugging: Print the initial maxNum and numberList at the start of each iteration
    print(f"Starting iteration with numberList: {numberList} and maxNum: {maxNum}")
    
    # Find the maximum number in numberList
    for num in numberList:
        if num > maxNum:
            maxNum = num
    
    # Debugging: Print the found maxNum
    print(f"Max number found: {maxNum}")
    
    # Add the maximum number to the sorted list
    sort_list.append(maxNum)
    
    # Remove the maximum number from the original list
    numberList.remove(maxNum)
    
    # Debugging: Print the updated numberList and sort_list after each iteration
    print(f"Updated numberList: {numberList}")
    print(f"Updated sort_list: {sort_list}")
    print("-----")

# Print the final results
print("Final sorted list:", sort_list)
