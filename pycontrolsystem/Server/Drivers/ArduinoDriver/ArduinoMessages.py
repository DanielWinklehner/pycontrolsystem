import time
import re


def build_set_message(channel_names, values_to_set):
    # Supports 1 message at at time only at the moment.

    # For reference: This is the message from the GUI:
    # device_data = {'device_driver': device_driver_name,
    #                'device_id': device_id,
    #                'locked_by_server': False,
    #                'channel_ids': [channel_ids],
    #                'precisions': [precisions],
    #                'values': [values],
    #                'data_types': [types]}

    if values_to_set[0] == "True":
        values_to_set[0] = "1"
    elif values_to_set[0] == "False":
        values_to_set[0] = "0"

    msg = "s"
    msg += str(channel_names[0])
    msg += str(values_to_set[0])

    return [(str(msg), 1)]


def output_message_per_channel_length(precision):
    sign = 1
    channel_name = 2
    mentissa = 1
    exponent = 1
    exponent_sign = 1
    per_channel_length = channel_name + sign + mentissa + int(precision) + exponent + exponent_sign

    return per_channel_length


def calculate_expected_output_message_length(precisions):
    message_identifier = 1  # The "o" at the beginning.
    number_of_channels = 2  # 2 because if it is < 10, then it gets padded with a precedding zero.

    total_length = message_identifier + number_of_channels + sum(
        [output_message_per_channel_length(precision) for precision in precisions])

    return total_length



def split_query_message(channel_ids, precisions):
    message_identifier = 1  # The "o" at the beginning.
    number_of_channels = 2  # 2 because if it is < 10, then it gets padded with a precedding zero.

    message_length = message_identifier + number_of_channels

    # Keep adding channels to query until you reach message_length == 127.

    indices_to_split_after = []
    for i in range(len(channel_ids)):
        # Length that current channel would give.
        current_channel_msg_length = output_message_per_channel_length(precisions[i])

        message_length += current_channel_msg_length

        # print "message length is", message_length, "vs.", 127

        if message_length > 127:
            # print "I think I'm gonna split."
            indices_to_split_after.append(i)

            message_length = message_identifier + current_channel_msg_length

    split_channels = []
    split_precisions = []

    split_from = 0
    for index_to_split_after in indices_to_split_after:
        split_channels.append(channel_ids[split_from: index_to_split_after])
        split_precisions.append(precisions[split_from: index_to_split_after])

        split_from = index_to_split_after

    # Finally, add the remainder.
    split_channels.append(channel_ids[split_from:])
    split_precisions.append(precisions[split_from:])

    # print split_channels, len(split_channels)
    # print split_precisions, len(split_precisions)

    all_messages_less_than_128_bytes = [1 if calculate_expected_output_message_length(precisions) else 0 for precisions
                                        in split_precisions]

    if len(all_messages_less_than_128_bytes) != len(split_channels):
        raise Exception("ERROR: One or more of the split message is going to be > 128 bytes long. Please fix the bug.")
    else:
        return split_channels, split_precisions



def build_query_message(channel_ids, precisions, safe_messages=[]):
    if len(channel_ids) != len(precisions):
        raise Exception("Number of channel names to query does not match the number of precisions requested.",
                        len(channel_ids), len(precisions))

    # Here, make sure that we don't send a message that gives us an output that's more than 128 characters long.
    # If the message seems to be that way, split it into smaller messages.

    # First, calculate the expected length of the output message.
    total_length = calculate_expected_output_message_length(precisions)

    if total_length > 127:
        # We need to split our message into smaller chunks.

        split_channels, split_precisions = split_query_message(channel_ids, precisions)

        all_messages = []
        for split_channel, split_precision in zip(split_channels, split_precisions):
            # return build_query_message(split_channel, split_precision, safe_messages=[])
            all_messages.append(build_query_message(split_channel, split_precision))

        return [(msg[0], 1) for msg in all_messages]

    else:
        msg = "q"
        msg += "{0:0>2}".format(len(channel_ids))

        for channel_name, precision in zip(channel_ids, precisions):
            msg += "{}{}".format(channel_name, precision)

        return [(msg, 1)]


arduino_error_messages_dict = {'ERR0': "Undefined error (does not fall into any of the other 9 categories).",
                               'ERR1': "Asking a precision that's too high (> 6).",
                               'ERR2': "Asking for something that would return more than 128 bytes.",
                               'ERR3': "Invalid number of channels.",
                               'ERR4': "Querying for one or more non-existing channel/s."}


def parse_arduino_output_message(output_messages):
    result = {}
    for output_message in output_messages:

        if "ERR" in output_message:
            error_key = output_message.split("\r\n")[0]
            raise Exception(error_key, arduino_error_messages_dict[error_key])
        else:

            parsed_message = ""

            # Everybody stand back. I know regular expressions.
            pattern = "([a-zA-Z][0-9])([\+\-])([0-9])([0-9]+)([0-9])([\+\-])"

            matches = re.findall(pattern, output_message, flags=0)

            for match in matches:
                channel_name = match[0]

                value = float("{}.{}".format(match[2], match[3]))

                if match[5] == "+":
                    value *= 10 ** (int(match[4]))
                elif match[5] == "-":
                    value *= 10 ** (- int(match[4]))

                if match[1] == "-":
                    value = 0 - value

                result[channel_name] = value

    return result
