import string
import subprocess
import random
import re
import winreg


def get_mac_transport_name() -> list:
    # fun to get MAC address and transport name from interfaces
    get_interfaces_info = subprocess.run(
        "getmac", capture_output=True).stdout.decode().split('\n')
    # using {subprocess.run()} to run a {getmac} command and capture the output
    # of this command that will be string data type and using
    # {stdout.decode()} to organize this output
    # using {split()} to separate the string output into a list data type
    mac_address_regex = re.compile(r"([\w]{2}[:-]){5}(\w{2})")
    # create MAC address regular expression and compile it into
    # object to find the MAC address using {re}
    transport_name_regex = re.compile(r"({.+})")
    # create transport name regular expression and compile it into
    # object to find the transport name for interface
    interfaces_macs_and_transport_name = list()
    # create a list to save the MAC address and transport name
    for find_mac_and_prot_name in get_interfaces_info:
        # for loop to loop into list of interfaces info
        # and search for MAC address and transport name
        # for interfaces
        search_result_for_interfaces_macs = mac_address_regex.search(
            find_mac_and_prot_name
        )
        # use {search()} method from {re.compile()} class
        # to find MAC address regex {search()} method accept
        # string argument so we loop into getmac list output
        # and compare every single string element inside the list
        search_result_for_trans_port_name = transport_name_regex.search(
            find_mac_and_prot_name
        )
        # same as MAC address search above
        if (search_result_for_interfaces_macs != None and search_result_for_trans_port_name != None):
            # the result from object method some time it will be None
            # or it will be group of object if the one of above is None
            # the condition will ignore the result and continue in the loop
            interfaces_macs_and_transport_name.append(
                (
                    search_result_for_interfaces_macs.group(0),
                    search_result_for_trans_port_name.group(0)
                )
            )
            # save the MAC address and transport name for the interfaces
            # as tuple inside the list the final result
    return interfaces_macs_and_transport_name


def gen_rand_mac() -> list:
    # fun to generate random mac address
    second_digit_for_mac = '26EA'
    # notice windows os MAC address second hexdigits should be
    # one of this digits 2, 6, A, E so be sure that second digit
    # one of this digit
    # and first number should be 0 im not sure from that
    uppercase_hexdigits = ''.join(set(string.hexdigits.upper()))
    # get hexdigits from string module and to be sure the digits
    # is uniq and not duplicate we pass them throw set data type
    mac_list, mac, num_of_mac_gen, mac_len = list(), '', 8, 12
    # create some variables
    for i in range(num_of_mac_gen):
        # loop to generate 8 MAC address
        for j in range(mac_len):
            # loop crouse of len of MAC address MAC len -> 12
            if j == 0:
                mac += '0'
                continue
            if j == 1:
                mac += random.choice(second_digit_for_mac)
                continue
            mac += random.choice(uppercase_hexdigits)
        mac_list.append(mac)
        # list of MACs
        mac = ''
    return mac_list


def disable_enable_adapter(mac_to_change_to, update_option):
    # We create regex to pick out the adapter index
    adapterIndex = re.compile("([0-9]+)")
    # Code to disable and enable Wireless devicess
    run_disable_enable = input(
        "Do you want to disable and reenable your wireless device(s). Press Y or y to continue:"
    )
    # Changes the input to lowercase and compares to y.
    # If not y the while function which contains the last part will never run.
    if run_disable_enable.lower() == 'y':
        run_last_part = True
    else:
        run_last_part = False

    # run_last_part will be set to True or False based on above code.
    while run_last_part:

        # Code to disable and enable the network adapters
        # We get a list of all network adapters. You have to ignore errors, as it doesn't like the format the command returns the data in.
        network_adapters = subprocess.run(
            ["wmic", "nic", "get", "name,index"],
            capture_output=True
        ).stdout.decode('utf-8', errors="ignore").split('\r\r\n')
        for adapter in network_adapters:
            # We get the index for each adapter
            adapter_index_find = adapterIndex.search(adapter.lstrip())
            # If there is an index and the adapter has wireless in description we are going to disable and enable the adapter
            if adapter_index_find and "Wireless" in adapter:
                disable = subprocess.run(
                    [
                        "wmic", "path", "win32_networkadapter", "where",
                        f"index={adapter_index_find.group(0)}", "call", "disable"
                    ],
                    capture_output=True
                )
                # If the return code is 0, it means that we successfully disabled the adapter
                if (disable.returncode == 0):
                    print(f"Disabled {adapter.lstrip()}")
                # We now enable the network adapter again.
                enable = subprocess.run(
                    ["wmic", "path", f"win32_networkadapter", "where",
                     f"index={adapter_index_find.group(0)}", "call", "enable"
                     ],
                    capture_output=True
                )
                # If the return code is 0, it means that we successfully enabled the adapter
                if (enable.returncode == 0):
                    print(f"Enabled {adapter.lstrip()}")

        # We run the getmac command again
        getmac_output = subprocess.run(
            "getmac", capture_output=True).stdout.decode()
        # We recreate the Mac Address as ot shows up in getmac XX-XX-XX-XX-XX-XX
        # format from the 12 character string we have. We split the string into strings of length 2 using list
        # comprehensions and then. We use "-".join(list) to recreate the address
        mac_add = "-".join([(mac_to_change_to[int(update_option)][i:i+2])
                           for i in range(0, len(mac_to_change_to[int(update_option)]), 2)])
        # We want to check if Mac Address we changed to is in getmac output, if so we have been successful.
        if mac_add in getmac_output:
            print("Mac Address Success")
        # Break out of the While loop. Could also change run_last_part to False.
        break


def mac_changer():
    mac_addresses = get_mac_transport_name()
    # Create a simple menu to select which Mac Address the user want to update.
    print("Which MAC Address do you want to update?")
    for index, item in enumerate(mac_addresses):
        print(
            f"[+] {index} - Mac Address: {item[0]} - Transport Name: {item[1]}"
        )
    # Prompt the user to select Mac Address they want to update.
    option = input(
        "[+] Select the menu item number corresponding to the MAC that you want to change: "
    )
    mac_to_change_to = gen_rand_mac()
    # Create a simple menu so the user can pick a MAC address to use
    while True:
        print(
            "Which MAC address do you want to use? This will change the Network Card's MAC address."
        )
        for index, item in enumerate(mac_to_change_to):
            print(f"{index} - Mac Address: {item}")
        # Prompt the user to select the MAC address they want to change to.
        update_option = input(
            "Select the menu item number corresponding to the new MAC address that you want to use:"
        )
        # Check to see if the option the user picked is a valid option.
        if int(update_option) >= 0 and int(update_option) < len(mac_to_change_to):
            print(
                f"Your Mac Address will be changed to: {mac_to_change_to[int(update_option)]}"
            )
            break
        else:
            print("You didn't select a valid option. Please try again!")
    # We know the first part of the key, we'll append the folders where we'll search the values
    controller_key_part = r"SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
    # We connect to the HKEY_LOCAL_MACHINE registry. If we specify None,
    # it means we connect to local machine's registry.
    with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
        # Create a list for the 21 folders. I used a list comprehension. The expression part of the list comprehension
        # makes use of a ternary operator. The transport value for you Mac Address should fall within this range.
        # You could write multiple lines.
        controller_key_folders = [
            ("\\000" + str(item) if item < 10 else "\\00" + str(item)) for item in range(0, 21)
        ]
        # We now iterate through the list of folders we created.
        for key_folder in controller_key_folders:
            # We try to open the key. If we can't we just except and pass. But it shouldn't be a problem.
            try:
                # We have to specify the registry we connected to, the controller key
                # (This is made up of the controller_key_part we know and the folder(key) name we created
                # with the list comprehension).
                with winreg.OpenKey(hkey, controller_key_part + key_folder, 0, winreg.KEY_ALL_ACCESS) as regkey:
                    # We will now look at the Values under each key and see if we can find the "NetCfgInstanceId"
                    # with the same Transport Id as the one we selected.
                    try:
                        # Values start at 0 in the registry and we have to count through them.
                        # This will continue until we get a WindowsError (Where we will then just pass)
                        # then we'll start with the next folder until we find the correct key which contains
                        # the value we're looking for.
                        count = 0
                        while True:
                            # We unpack each individual winreg value into name, value and type.
                            name, value, type = winreg.EnumValue(regkey, count)
                            # To go to the next value if we didn't find what we're looking for 
                            # we increment count.
                            count += 1
                            # We check to see if our "NetCfgInstanceId" is equal to our Transport number for our
                            # selected Mac Address.
                            if name == "NetCfgInstanceId" and value == mac_addresses[int(option)][1]:
                                new_mac_address = mac_to_change_to[int(
                                    update_option)]
                                winreg.SetValueEx(
                                    regkey, "NetworkAddress", 0, winreg.REG_SZ, new_mac_address)
                                print("Successly matched Transport Number")
                                # get list of adapters and find index of adapter you want to disable.
                                disable_enable_adapter(
                                    mac_to_change_to, update_option
                                )
                                break
                    except WindowsError:
                        pass
            except:
                pass


if __name__ == '__main__':
    print("##############################################################")
    print("1) Make sure you run this script with administrator privileges")
    print("2) Make sure that the WiFi adapter is connected to a network")
    print("##############################################################\n")
    mac_changer()
