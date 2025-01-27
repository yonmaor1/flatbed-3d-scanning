import argparse

def main():
    parser = argparse.ArgumentParser(description='Process an input file.')
    parser.add_argument('-i', '--input', required=True, help='Input file path')
    args = parser.parse_args()
    
    input_file = args.input

    with open(input_file, 'r') as file:
        file_lines = file.readlines()
        for line in file_lines:
            line_args = line.split(' ')

            if line_args[0] == 'f':
                print('found polygonal entry, finishing...')
                with open('amped_object.obj', 'a') as output_file:
                    output_file.writelines(file_lines[file_lines.index(line):])
                
                break

            line_args[-1] *= 10
            new_line = ' '.join(line_args)
            with open('amped_object.obj', 'a') as output_file:
                output_file.write(new_line + '\n')



if __name__ == '__main__':
    main()