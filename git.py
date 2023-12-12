import os
import pandas as pd
import io
import csv
import re

def get_orca_out_filename():
    # List all files in the current directory
    files_in_directory = os.listdir(os.getcwd())

    # Filter files that end with ".out"
    orca_out_files = [file for file in files_in_directory if file.endswith(".out")]

    # Check if there is exactly one .out file in the directory
    if len(orca_out_files) == 1:
        return orca_out_files[0]
    elif len(orca_out_files) == 0:
        print("Error: No .out file found in the directory.")
    else:
        print("Error: More than one .out file found in the directory.")
    return None

def copy_text_between_strings(content, start_string, end_string):
    start_index = content.find(start_string)
    end_index = content.find(end_string, start_index + len(start_string))

    if start_index == -1 or end_index == -1:
        print("Text not found between the provided strings.")
        return None

    selected_text = content[start_index:end_index].strip()
    return selected_text

def remove_lines(text):
    lines = text.split('\n')

    # Check if there are at least 3 lines
    if len(lines) < 3:
        print("The text does not have enough lines to be removed.")
        return None

    # Remove the second and third lines
    lines.pop(1)  # Remove the second line
    lines.pop(1)  # After removing the second line, the third line now occupies position 1

    modified_text = '\n'.join(lines)
    print("Second and third lines successfully removed!")
    return modified_text

def remove_space_after_opening_parentheses(text):
    lines = text.split('\n')
    modified_lines = []

    for line in lines:
        line = line.replace('( ', '(')  # Remove space after "( "
        modified_lines.append(line)

    modified_text = '\n'.join(modified_lines)
    print("Spaces after opening parentheses successfully removed!")
    return modified_text

def convert_txt_to_csv_in_memory(text):
    # Process the content and return a pandas DataFrame
    lines = text.split('\n')
    data = [line.strip().split() for line in lines]
    df = pd.DataFrame(data)
    return df

def replace_text_in_dataframe(dataframe, old_text, new_text):
    # Replace text in the DataFrame
    dataframe.replace(old_text, new_text, inplace=True)
    print(f"Text '{old_text}' replaced with '{new_text}' in the DataFrame.")

def remove_columns_in_memory(content, columns_to_remove):
    # Create an in-memory file object
    input_file = io.StringIO(content)
    output_file = io.StringIO()

    csv_reader = csv.reader(input_file)
    csv_writer = csv.writer(output_file)

    for row in csv_reader:
        # Remove the specified columns in columns_to_remove
        new_row = [col for idx, col in enumerate(row) if idx not in columns_to_remove]
        csv_writer.writerow(new_row)

    # Get the modified content from the in-memory output
    result = output_file.getvalue()

    return result

def convert_csv_to_out_in_memory(csv_content):
    # Create an in-memory file object
    csvfile = io.StringIO(csv_content)
    outfile = io.StringIO()

    csv_reader = csv.DictReader(csvfile)
    fieldnames = csv_reader.fieldnames

    out_writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=' ')
    out_writer.writeheader()

    for row in csv_reader:
        # You can perform manipulations on the values here if necessary.
        # In this example, we will just copy the values as they are.
        out_writer.writerow(row)

    # Get the modified content of the I_R.out file from the in-memory output
    result = outfile.getvalue()

    return result

def modify_file_in_memory(text):
    new_first_line = "Mode    freq (cm**-1)   T**2         TX         TY         TZ\n"
    separator_line = "----------------------------------------------------------------------------\n"

    lines = text.split('\n')
    if len(lines) > 0:
        lines[0] = new_first_line
        if len(lines) > 1:
            lines.insert(1, separator_line)

            # Find indices of lines between separator_line and new_first_line that are empty or start with "Mode freq T**2" and remove them
            indices_to_remove = [i for i, line in enumerate(lines) if separator_line in line and new_first_line in lines[i+1:i+3]]
            indices_to_remove += [i for i in range(len(lines)) if lines[i].startswith("Mode freq T**2") or lines[i].isspace()]

            for idx in reversed(indices_to_remove):
                lines.pop(idx)

    modified_text = '\n'.join(lines)
    print("File modified successfully!")
    return modified_text

def duplicate_and_modify_orca_out(original_file, csv_content):
    try:
        # Get the filename without the extension
        base_name, _ = os.path.splitext(original_file)

        # Build the copied file name with modification
        copied_file = f"{base_name}_modified.out"

        # Copy content from the original .out file to the copied file
        with open(original_file, 'r') as original:
            original_content = original.read()

        with open(copied_file, 'w') as copied:
            copied.write(original_content)

        # Use regular expressions (regex) to find the section to be removed and paste content
        pattern_to_remove = r'Mode\s+freq\s+eps(.*?)(?:\n\s*\n|$)'
        matches = re.finditer(pattern_to_remove, original_content, flags=re.DOTALL)

        for match in matches:
            section_to_remove = match.group(0)
            start_section = match.start()
            end_section = match.end()
            modified_content = original_content[:start_section] + csv_content.strip() + "\n\n" + original_content[end_section:]

        # Find the "IR SPECTRUM" line and remove the 4th and 6th lines after it
        modified_lines = modified_content.split('\n')
        for i, line in enumerate(modified_lines):
            if line.startswith("IR SPECTRUM"):
                if i + 5 < len(modified_lines):
                    modified_lines.pop(i + 4)  # Remove the 6th line after "IR SPECTRUM"
                if i + 3 < len(modified_lines):
                    modified_lines.pop(i + 2)  # Remove the 4th line after "IR SPECTRUM"
                    modified_lines.pop(i + 4)
                    modified_lines.insert(i + 2, "")
			
        modified_content = '\n'.join(modified_lines)

        # Write the copied content to the modified .out file
        with open(copied_file, 'w') as copied:
            copied.write(modified_content)

        print(f"File duplicated as '{copied_file}' and modifications successfully made.")
    except Exception as e:
        print(f"Error duplicating and modifying the .out file: {e}")

if __name__ == "__main__":
    orca_out_filename = get_orca_out_filename()

    if orca_out_filename:
        with open(orca_out_filename, 'r') as infile:
            orca_content = infile.read()

        start_string = "Mode   freq"
        end_string = "* The"

        selected_text = copy_text_between_strings(orca_content, start_string, end_string)

        if selected_text:
            modified_text = remove_lines(selected_text)
            modified_text = remove_space_after_opening_parentheses(modified_text)

            # Convert the modified text to a pandas DataFrame
            df = convert_txt_to_csv_in_memory(modified_text)

            old_text = "Int"
            new_text = "T**2"

            # Replace text directly in the DataFrame
            replace_text_in_dataframe(df, old_text, new_text)

            # Remove columns in memory
            columns_to_remove = [2, 4]  # Indices of columns to be removed (remembering that index starts at 0)
            result = remove_columns_in_memory(df.to_csv(index=False), columns_to_remove)

            # Convert CSV to OUT in memory
            final_result = convert_csv_to_out_in_memory(result)

            # Modify file in memory
            final_result = modify_file_in_memory(final_result)

            # Duplicate .out file and make modifications in the copy
            duplicate_and_modify_orca_out(orca_out_filename, final_result)

