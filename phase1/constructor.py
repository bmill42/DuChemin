#!/usr/bin/python

from scripts import *
import sys
import os
import time
import random
import json

if __name__ == "__main__":
    #Scripting Variable Setup.
    clean = False
    normalize = False
    regress = True
    show_regressions = False
    show_extra_output = True
    random_sampling = False
    calculate_r2 = False
    create_kd_tree = False
    remove_cols = False
    default = False
    sample_size = 0
    csv_file_input = ""
    file_output = {}
    data_dir = "output/"
    cols_to_remove = []
    last_command = ""  # Used to keep track of kwarg arguments.

    #Translate the sys.args following "python constructor.py".
    for arg in sys.argv[sys.argv.index("constructor.py")+1:]:
        lower_arg = arg.lower()
        #Display the "help menu" if the user requests it.
        if (lower_arg.replace("-", "") == "help" or
                lower_arg.replace("-", "") == "h"):
            display_help()

        elif arg[:2] == "--":
            if lower_arg == "--clean":
                clean = True
            elif lower_arg == "--normalize":
                normalize = True
            elif lower_arg == "--no-regressions":
                regress = False
            elif lower_arg == "--show-regressions":
                show_regressions = True
            elif lower_arg == "--hide-extra-output":
                show_extra_output = False
            elif lower_arg == "--random-sampling":
                random_sampling = True
            elif lower_arg == "--calculate-r2":
                calculate_r2 = True
            elif lower_arg == "--create-kd-tree":
                create_kd_tree = True
            elif lower_arg == "--remove-cols":
                remove_cols = True
            elif lower_arg == "--default":
                if not csv_file_input:
                    fatal_error("Tried default options, " +
                                "but no input CSV specified.")

                #Get a valid file root name.
                filename = csv_file_input[:csv_file_input.index(".")]
                if "/" in filename:
                    filename = filename[filename.rfind("/")+1:]

                default = True
                show_regressions = True
                random_sampling = True
                calculate_r2 = True
                file_output["regressions"] = "REGRESSIONS_{}.json".format(filename)
                file_output["samples"] = "SAMPLES_{}.json".format(filename)
                file_output["r2"] = "R2_{}.json".format(filename)
                sample_size = 400

            else:
                fatal_error("Encountered unknown argument: {}\n".format(arg))

            last_command = lower_arg
        else:
            if last_command == "" and not csv_file_input:
                csv_file_input = arg
            elif last_command == "--clean" and not file_output.get("clean"):
                file_output["clean"] = arg
            elif (last_command == "--normalize" and
                    not file_output.get("clean")):
                file_output["clean"] = arg
            elif (last_command == "--remove-cols" and
                    not file_output.get("clean")):
                file_output["clean"] = arg
                last_command = "--remove-cols N"
            elif last_command == "--remove-cols N":
                if is_number(arg) and int(float(arg)) >= 0:
                    cols_to_remove.append(int(float(arg)))
            elif (last_command == "--show-regressions" and
                    not file_output.get("regressions")):
                file_output["regressions"] = arg
            elif (last_command == "--calculate-r2" and
                    not file_output.get("r2")):
                file_output["r2"] = arg
            elif (last_command == "--create-kd-tree" and
                    not file_output.get("kd_tree")):
                file_output["kd_tree"] = arg
            elif last_command == "--random-sampling" and not sample_size:
                if is_number(arg) and int(float(arg)) > 0:
                    sample_size = int(float(arg))
                    last_command = "--random-sampling N"
                else:
                    fatal_error("First argument of `--random-sampling` " +
                                "must be a positive number.")
            elif (last_command == "--random-sampling N"
                    and not file_output.get("samples")):
                file_output["samples"] = arg
            elif last_command == "--default":
                data_dir += arg

                #Fix the forward-slashes in the data_directory.
                if data_dir[-1] != "/":
                    data_dir += "/"
                data_dir = data_dir.replace("//", "/")

                #Create the new directory.
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)

            else:
                fatal_error("Unknown argument sent to keyword `{}`: {}\n".format(last_command, arg))

    if default:
        msg = "The following files will be written or replaced in \"./{}\":".format(data_dir)
        for filename in file_output.values():
            msg += "\n\t{}".format(filename)
        msg += "\nAre you sure? (y/n)\n"

        if not user_verify(msg):
            sys.exit()

    #Before scripts are run, validate the input.
    if not csv_file_input:
        fatal_error("No CSV input specified (use `python constructor.py INPUT_FILE`).")
    if random_sampling and not sample_size:
        fatal_error("Random sampling requested, but no size indicated.")
    if calculate_r2 and not regress:
        fatal_error("R-squared calculation requires linear regression (remove option \"--no-regressions\").")

    #Sub-functionality of script: rewrite a CSV without a series of columns.
    if remove_cols:
        data_list = get_data_without_cols(csv_file_input, cols_to_remove)
        write_data("{}{}".format(data_dir, file_output["clean"]),
                   data_list[0], data_list[1:])
        print "File write complete..."
        sys.exit()

    #Start the time counter.
    t_start = time.time()

    #Load data_dict and data_list. Clean it if requested.
    message("Reading CSV...", show=show_extra_output)
    data_list = get_data_list(csv_file_input, clean=clean, normalize=normalize)
    headers = get_headers(csv_file_input)

    #Write the cleaned CSV if applicable.
    if file_output.get("clean"):
        message("Creating new CSV...", show=show_extra_output)
        write_data("{}{}".format(data_dir, file_output["clean"]),
                   headers, data_list)

    if random_sampling:
        message("Gathering random samples...", show=show_extra_output)
        samples = random.sample(data_list, sample_size)
        if file_output.get("samples"):
            with open("{}{}".format(data_dir, file_output["samples"]),
                      "w") as f:
                json.dump([headers]+samples, f)
        else:
            print [headers]+samples

    if regress:
        message("Starting Linear Regressions...", show=show_extra_output)

        if not check_version():
            fatal_error("Your Python version does not support " +
                        "linear regressions. Please use 2.7+")

        regressions, r2_dict = get_linear_regressions(headers, data_list,
                                                      calc_r2=calculate_r2)
        if show_regressions:
            message("Preparing regression output...", show=show_extra_output)
            if file_output["regressions"]:
                with open("{}{}".format(data_dir,
                                        file_output["regressions"]), "w") as f:
                    json.dump(arrayDict_to_listDict(regressions), f)
            else:
                print json.dumps(arrayDict_to_listDict(regressions))

        if calculate_r2:
            message("Preparing R-squared output...", show=show_extra_output)
            if file_output.get("r2"):
                with open("{}{}".format(data_dir,
                                        file_output["r2"]), "w") as f:
                    json.dump(r2_dict, f)
            else:
                print r2_dict

    if create_kd_tree:
        message("Preparing KD-Tree...", show=show_extra_output)
        #Create a KDTree by cutting the initial dataset by the first column.
        kd_tree = hyperspace_partitioner(headers, 0, data_list)
        if file_output.get("kd_tree"):
            with open("{}{}".format(data_dir,
                                    file_output["kd_tree"]), "w") as f:
                f.write(str(kd_tree))
        else:
            print kd_tree

    message("Finished ({} seconds)!".format(time.time()-t_start),
                                            show=show_extra_output)
