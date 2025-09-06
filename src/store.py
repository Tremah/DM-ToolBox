def generateDieRanges():
  # Read data from probabilities text box
  probabilities = probabilityInputText.get('1.0', 'end')

  # Remove empty lines
  items = []
  for item in probabilities.split('\n'):
    if item != '':
      items.append(int(item))

  # Check data
  logOutputText.delete('1.0', 'end')
  logOutputText.configure(state='normal')

  if len(items) < 1:
    logOutputText.insert('end', 'No probabilities given\n')
    return

  probSum = 0
  for item in items:
    probSum += int(item)

  if probSum != 100:
    logOutputText.insert('end', 'Probabilities are less or more than 100\n')
    return

  logOutputText.configure(state='disabled')

  ##Calculate dice ranges from probabilities

  # Clear output text box
  dieRangesOutputText.delete('1.0', 'end')
  start = int(dieAmountEntry.get())
  dieNumber = int(dieSelection.get()[1:len(dieSelection.get())])
  dieMaxNumber = dieNumber * int(dieAmountEntry.get())

  for item in items:
    percentageOfDieValue = round(dieMaxNumber * (item * 0.01))
    end = start + percentageOfDieValue

    if percentageOfDieValue > 1:
      end -= 1

    if end > dieMaxNumber:
      end = dieMaxNumber

    rangeStr = str(start) + '-' + str(end) + '\n'
    dieRangesOutputText.insert('end', rangeStr)
    start = end + 1