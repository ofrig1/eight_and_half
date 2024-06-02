import logging
import traceback

SEPERATOR = '|'


def protocol_receive(my_socket):
    """
    Protocol to receive message from client to server
    :param my_socket:
    :return: message sent from client
    """
    final_message = ''
    try:
        cur_char = ''
        message_len = ''
        while cur_char != SEPERATOR:
            cur_char = my_socket.recv(1).decode()
            if cur_char != SEPERATOR:
                message_len += cur_char
        for i in range(int(message_len)):
            final_message += my_socket.recv(1).decode()
        if SEPERATOR in final_message:
            final_message = final_message.split(SEPERATOR, 1)[1]
        return final_message
    except ConnectionResetError as e:
        print(f"Connection was reset: {e}")
        raise
    except Exception as e:
        stack_trace = traceback.format_exc()
        print(stack_trace)
        print(f"Error: {e}. Server failed to receive client message")
        raise


def protocol_client_send(message):
    """
    send message with protocol
    :param message: message to be sent
    :return: message after protocol
    """
    try:
        message_len = len(message)
        final_message = str(message_len) + SEPERATOR + message
        return final_message
    except Exception as e:
        logging.info(traceback.format_exc())
        return f"Error: {e}. Client message failed to send to server with protocol"
