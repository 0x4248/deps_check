# Deps test
# Run a set of tests or checks to see if commands run successfully or files exist
# GitHub: https://www.github.com/0x4248/deps_check
# Licence: GNU General Public License v3.0
# By: 0x4248

import os
import sys
import subprocess

from deps_check import colors
from deps_check import characters

VERSION = "0.1"
silent = False


def parse_file(file_name):
    targets = {}
    rules = {}
    file = open(file_name, "r")
    file = file.readlines()
    in_rule = False
    rule_name = ""

    for line in file:
        if line.startswith("#"):
            continue

        if line.startswith("%"):
            line = line[1:]
            target = line.split(":")
            targets[target[0]] = target[1].split()
            continue
        if line.endswith(":\n") and not in_rule:
            in_rule = True
            rule_name = line[:-2]
            rules[rule_name] = []
            continue
        if in_rule:
            if line == "\n":
                in_rule = False
                continue
            if line[4:].startswith("#"):
                continue
            rules[rule_name].append(line.replace("\n", "")[4:])

            continue
    return targets, rules


def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return 0, output
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output


def print_fail_report(report):
    for i in range(len(report["Rules_ran"])):
        if "FAIL" in report["Status"][i]:
            print(
                colors.RED
                + characters.CROSS
                + " "
                + report["Rules_ran"][i]
                + colors.RESET
            )
            for j in range(len(report["Reports"][i]["Commands_ran"])):
                if "FAIL" in report["Reports"][i]["Status"][j]:
                    print(
                        "    "
                        + colors.RED
                        + characters.CROSS
                        + " "
                        + report["Reports"][i]["Commands_ran"][j]
                        + colors.RESET
                    )
                    if report["Reports"][i]["Command_type"][j] == "Command":
                        print(
                            "        Command returned: "
                            + str(report["Reports"][i]["Exit_code"][j])
                        )
                    if report["Reports"][i]["Command_type"][j] == "Not Command":
                        print(
                            "        Command returned 0 exit code but expected a non-zero exit code"
                        )
                    print("        " + str(report["Reports"][i]["Output"][j]))


def print_fail():
    if not silent:
        print(
            "["
            + colors.RED
            + characters.CROSS
            + colors.RESET
            + "]"
            + colors.RED
            + " FAIL"
            + colors.RESET
        )


def print_pass():
    if not silent:
        print(
            "["
            + colors.GREEN
            + characters.TICK
            + colors.RESET
            + "]"
            + colors.GREEN
            + " PASS"
            + colors.RESET
        )


def run_target(rules, targets, target):
    reports = {
        "Rules_ran": [],
        "Reports": [],
        "Status": [],
    }
    for rule in targets[target]:
        print("==== Running Rule: " + rule + " ====")
        report = run_rule(rules, targets, rule)
        reports["Rules_ran"].append(rule)
        reports["Reports"].append(report)
        if "FAIL" in report["Status"]:
            reports["Status"].append("FAIL")
        else:
            reports["Status"].append("PASS")
    print_fail_report(reports)


def run_rule(rules, targets, rule_to_run):
    report = {
        "Commands_ran": [],
        "Status": [],
        "Output": [],
        "Exit_code": [],
        "Command_type": [],
    }

    for rule in rules[rule_to_run]:
        if rule.startswith("!"):
            rule = rule[1:]
            if rule.startswith("$"):
                command = rule[1:]
                report["Commands_ran"].append(command)
                report["Command_type"].append("Not Command")
                ret, output = run_command(command)
                if ret == 0:
                    print_fail()
                    report["Status"].append("FAIL")
                    report["Output"].append(output)
                    report["Exit_code"].append(0)
                    continue
                else:
                    print_pass()
                    report["Status"].append("PASS")
                    report["Output"].append(output)
                    report["Exit_code"].append(1)
                    continue
            if rule.startswith("@"):
                file = rule[1:]
                report["Commands_ran"].append(file)
                report["Command_type"].append("Not File")
                if os.path.exists(file):
                    print_fail()
                    report["Status"].append("FAIL")
                    report["Output"].append("File Exists")
                    report["Exit_code"].append(1)
                    continue
                else:
                    print_pass()
                    report["Status"].append("PASS")
                    report["Output"].append("File Does Not Exist")
                    continue
        if rule.startswith("$"):
            command = rule[1:]
            report["Commands_ran"].append(command)
            report["Command_type"].append("Command")
            ret, output = run_command(command)
            report["Output"].append(output)
            report["Exit_code"].append(ret)
            if ret != 0:
                print_fail()
                report["Status"].append("FAIL")
                continue
            else:
                print_pass()
                report["Status"].append("PASS")
                continue
        if rule.startswith("@"):
            file = rule[1:]
            report["Commands_ran"].append(file)
            report["Command_type"].append("File")
            if os.path.exists(file):
                print_pass()
                report["Status"].append("PASS")
                report["Output"].append("File Exists")
                continue
            else:
                print_fail()
                report["Status"].append("FAIL")
                report["Output"].append("File Does Not Exist")
                continue
    return report


def main():
    file = "deps.txt"
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-f" or sys.argv[i] == "--file":
            file = sys.argv[i + 1]
        if sys.argv[i] == "-h" or sys.argv[i] == "--help":
            print("deps_check -f <file>")
            sys.exit(0)
    targets, rules = parse_file(file)
    run_target(rules, targets, "all")


if __name__ == "__main__":
    main()
