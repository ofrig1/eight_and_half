"""
author: Ofri
Date: 01/06/24
description: skeleton server which handles multiple clients by using select
"""
import logging
import socket
import traceback

import select
import START
import protocol

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8820
LISTEN_SIZE = 5
num_of_players = 0
SEPERATOR = '$'


current_player = 0
game_state = "WAITING"


def send_deck_to_all_clients(decks, open_client_sockets, msg_type):
    """
    sends message to all players
    :param decks: decks to send to players
    :param open_client_sockets: list of clients to send message to
    :param msg_type: type of message (dek)
    :return:
    """
    player = 1
    for client_socket in open_client_sockets:
        message = decks[player - 1]
        message_str = msg_type + SEPERATOR + SEPERATOR.join(map(str, message))
        try:
            message_str = protocol.protocol_client_send(message_str)
            client_socket.send(message_str.encode())
            logging.info("sending deck message: " + message_str)
        except socket.error as e:
            logging.error(f"Error sending message to {client_socket.getpeername()}: {e}")
        player = player + 1


def send_new_card_to_all(msg, did_win, open_client_sockets, msg_type):
    """
    Send update to all players
    :param msg: message to send
    :param did_win: whether one of the players won
    :param open_client_sockets:
    :param msg_type:
    :return:
    """
    global current_player
    for client_socket in open_client_sockets:
        message_str = msg_type + SEPERATOR + str(did_win) + SEPERATOR + str(current_player) + SEPERATOR + msg
        print("sending new card to all (UPDATE MESSAGE)", message_str)
        message_str = protocol.protocol_client_send(message_str)
        try:
            client_socket.send(message_str.encode())
            logging.info("sending " + msg_type + " message: " + message_str)
        except socket.error as e:
            logging.info(traceback.format_exc())
            logging.error(f"Error sending message to {client_socket.getpeername()}: {e}")


def send_play(msg, msg_type, client_socket):
    message_str = msg_type + SEPERATOR + SEPERATOR.join(map(str, msg))
    try:
        client_socket.send(message_str.encode())
    except socket.error as e:
        logging.error(f"Error sending message to {client_socket.getpeername()}: {e}")


def receive_low_message_type(client_socket, msg_type, messages):
    try:
        data = protocol.protocol_receive(client_socket)
        if data:
            if not data.startswith(msg_type + SEPERATOR):
                raise ValueError("Invalid message format: Message does not start with 'low$'")
            logging.info("received LOW message : " + data)
            # Remove the leading '$' character
            data = data[4:]
            card_sent, ignore, player, ignore = data.split(SEPERATOR)
            # message, player = parse(data)
            messages[int(player) - 1] = card_sent
    except socket.error as e:
        print(f"Socket error: {e}")
    return messages


def pick_starting_player(lowest_cards):
    if not lowest_cards:
        raise ValueError("The list of cards is empty")
    lowest_card = min(lowest_cards)
    if lowest_card == 15:
        return 1
    return lowest_cards.index(lowest_card) + 1


def logout(current_socket, open_client_sockets):
    """
    perform logout for the user holding the current socket, remove the user
     from the open sockets list and close the socket
    :param current_socket: the socket to perform the operation on
    :param open_client_sockets: the list of open sockets
    # :param mngr: the user manager
    :return: None
    """
    # Close the socket
    current_socket.close()
    # Remove the socket from the list of open client sockets
    open_client_sockets.remove(current_socket)


def receive_don_message(my_socket):
    message_str = protocol.protocol_receive(my_socket)
    logging.info('received msg: ' + message_str)
    if not message_str:
        raise ValueError("Received empty message from server")
    if not message_str.startswith('DON$'):
        raise ValueError("Invalid message format: Message does not start with 'DON$'")
    message_str = message_str[4:]
    new_card_placed, did_win, player, did_turn = message_str.split(SEPERATOR)
    return new_card_placed, did_win, int(player), did_turn


def parse(msg):
    parts = msg.split(SEPERATOR, 1)
    if len(parts) < 1:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    current_card = parts[0]
    player = parts[1]
    return current_card, player


def send_client(client_socket, msg):
    msg = protocol.protocol_client_send(msg)
    logging.info('sending message: ' + msg)
    client_socket.send(msg.encode())


def turn(discard_pile, open_client_sockets, server_socket):
    # send_new_card_to_all("Empty", False, current_player, open_client_sockets, "UPD")
    global current_player
    global game_state
    did_win_bool = True
    did_turn_bool = True
    new_card_placed, did_win, player, did_turn = receive_don_message(server_socket)
    if did_win == "False":
        did_win_bool = False
    if did_turn == "False":
        did_turn_bool = False
    print("New Card Placed:", new_card_placed, "Did Win: ", did_win, "Player:", player, "Did Turn:", did_turn)
    player = int(player)
    current_player = int(current_player)
    if player != current_player:
        print("Received from wrong player")
    else:
        if did_win_bool is False:
            current_player = (current_player % num_of_players) + 1
        if did_turn_bool:
            discard_pile += new_card_placed
            send_new_card_to_all(new_card_placed, False, open_client_sockets, "UPD")
        else:
            send_new_card_to_all("EMPTY", False, open_client_sockets, "UPD")
        if did_win_bool is True:
            game_state = "WIN"
            logging.info('player ' + str(player) + "WON!")
            send_new_card_to_all(new_card_placed, True, open_client_sockets, "UPD")


def is_full(messages):
    for message in messages:
        if message is None:
            return False
    return True


def main_loop():
    """
    the main server loop, waits for messages from clients and acts according
    :return: None, endless loop
    """
    global num_of_players, current_player, game_state
    server_socket = socket.socket()
    discard_pile = []
    open_client_sockets = []
    send_sockets = []
    messages = [None] * num_of_players
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(LISTEN_SIZE)
        while True:
            rlist, wlist, xlist = select.select([server_socket]
                                                + open_client_sockets,
                                                send_sockets, open_client_sockets)
            # print(datetime.datetime.now())
            # check for exception
            # for current_socket in xlist:
            #     logging.info('handling exception socket')
            #     logout(current_socket, open_client_sockets, mngr)
            for current_socket in rlist:
                # check for new connection
                if current_socket is server_socket:
                    client_socket, client_address = current_socket.accept()
                    logging.info('received a new connection from '
                                 + str(client_address[0]) + ':'
                                 + str(client_address[1]))
                    open_client_sockets.append(client_socket)
                    if len(open_client_sockets) <= num_of_players and game_state == "WAITING":
                        # send_client(client_socket, "Connected")
                        player_num = len(open_client_sockets)
                        message_str = "NUM" + SEPERATOR + SEPERATOR.join(map(str, str(player_num)))
                        send_client(client_socket, message_str)
                        if player_num == num_of_players:
                            game_state = "PREP"
                            start = START.START(num_of_players)
                            # player_decks = start.create_cards()
                            player_decks = start.create_cards()
                            print(player_decks)
                            send_deck_to_all_clients(player_decks, open_client_sockets, 'DEK')
                    else:
                        send_client(client_socket, "Too Many Players: Unable to Connect")
                        logging.info("sending message : too many players")
                        logout(client_socket, open_client_sockets)

                else:
                    if game_state == "PREP":
                        logging.info("IN PREP")
                        lowest_cards = receive_low_message_type(current_socket, 'LOW', messages)
                        if is_full(messages):
                            print("All low messages received:", messages)
                            current_player = pick_starting_player(lowest_cards)
                            print("The starting player is player " + str(current_player))
                            # send_play(current_player, msg_type, client_socket)
                            send_new_card_to_all("EMPTY", False, open_client_sockets, "UPD")
                            game_state = "PLAY"
                    elif game_state == "PLAY":
                        logging.info("IN PLAY")
                        turn(discard_pile, open_client_sockets, current_socket)
                    elif game_state == "WIN":
                        logging.info("WIN")
                    # send win message
                    #     exit()

    except socket.error as err:
        logging.info('received socket error - exiting, ' + str(err))
    finally:
        server_socket.close()


def main():
    """
    Add Documentation here
    """
    global num_of_players
    num_of_players = int(input("How many people are playing? "))
    # makes sure # of players is valid (2-4)
    while num_of_players < 2 or num_of_players > 4:
        print("Invalid number of participants")
        num_of_players = int(input("How many people are playing? "))
    main_loop()


if __name__ == '__main__':
    logging.basicConfig(filename="server.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',)
    main()
