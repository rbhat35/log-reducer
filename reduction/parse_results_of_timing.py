import pandas as pd

data = pd.read_csv("results_expanded.csv", header=None)
data.columns = ['methodName', 'serial', 'time']

print "Total " + str(pd.to_numeric(data['time'], errors='coerce').sum()) + " in " + str(data.shape[0]) + " lines"


def printResults(methodName):
    matching = data.query('methodName == ' + methodName)
    print methodName + " " +  str(pd.to_numeric(matching['time'], errors='coerce').sum()) + " in " + str(matching.shape[0]) + " lines"

print("\n")
printResults('"check_overlap"')
printResults('"forward_check"')
printResults('"backward_check"')
printResults('"generate_children"')
printResults('"generate_parents"')
printResults('"make_final_csv"')
printResults('"merge"')
print("\n")
printResults('"reduction"')
printResults('"if_cond"')
printResults('"ordereddict"')
printResults('"parser"')
printResults('"just_append_to_stack"')
print("\nIn Two For Loops:")
printResults('"1_for_loop"')
printResults('"2_for_loop"')
printResults('"del_and_append"')
print("\n\n")