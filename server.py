from socket import AF_INET, socket, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from re import match

# A few colors that will be used in text messaging. This is not compatible with the Windows Terminal.
# You might try using Cmder instead (or any terminal compatible with ANSI Escape Sequences).

COLOR_SUPERADMIN = '\033[95m'
COLOR_ADMIN = '\033[91m'
COLOR_DEFAULT = '\033[39m'
COLOR_SYS = '\033[92m'
STYLE_DIM = '\033[2m'
STYLE_DIM_RESET = '\033[22m'


class Channel:
    ''' Is a channel with a name, and some members.

    • Attributes:
        name:           Its name, used by users to find the channel
        members:        All members, admins included
        admins:         Only the admin members                      '''
    
    def __init__(self, name):
        self.name = name
        self.members = []
        self.admins = []


class User:
    ''' Is a client socket, and many other information and methods.

    • Class attributes:
        instances:              A list of all the instances of the User class.
        channels:               A list of all channels' names.
        banned:                 A list of all banned users.

    • Attributes:
        sock:           The socket used to listening and sending data to the client.
        address:        The user's address. Used for banning someone.
        nickname:       Its nickname.
        format_nick:    The nickname, formatted (admin are in red, superadmin in magenta and others in the default color).
        current:        The current channel.
        superadmin:     Is this user a superadministrator?        
        
    • Methods:
        switch:                 Change user's current channel
        find_channel            Search for a channel according to its name and returns the channel object (or None if nothing's found)
        find_user:              Search for a user according to its name and returns the user object (or None if nothing's found)
        change_nick:            Change user's nickname
        refresh_format_nick     Refresh the formatted nickname (usuful if the person is no longer admin or was granted admin)
        kick                    Kick the user out of the current channel. He goes back to the Main channel.
        recv                    Wait to receive data from the users. The waiting state for the main loop used in handle_user.
        send                    Send a message to the user. You can use "sys = False" in the function call to diplay the message as a user message.
        send_channel            Send a message to everyone on the channel. You can use "to_self = False" to avoid sending the message to yourself.
        send_channels           Send a message to all channel the user has joined. You can use "to_current = False" to avoid sending it to the current channel.
        send_all                Send a message to everyone on the server.
        '''


    instances = []
    channels = [Channel('VOID'), Channel('MAIN')]
    banned = []

    def __init__(self, sock, address):
        self.sock = sock
        self.address = address[0]
        self.nickname = None
        self.format_nick = ''
        self.current = self.find_channel('VOID')
        self.current.members += [self]
        self.superadmin = False
        self.instances.append(self)

    def find_channel(self, name):
        for channel in self.channels:
            if channel.name == name:
                return channel
        
    def find_user(self, nick):
        for user in self.current.members:
            if user.nickname == nick:
                return user

    def switch(self, channel):
        
        self.current = channel
        self.refresh_format_nick()

        # Alert everyone on the channel that the user has joined.
        self.send('You are now in the channel "' + channel.name + '".\n')
        self.send_channel(self.format_nick + ' has joined the channel!', to_self = False, to_currents_only = True)
        

    def change_nick(self, nickname):
        # Make sure the nickname has a correct form (alphanumerical characters only and no spaces)
        if not bool(match('^[a-zA-Z0-9]+$', nickname)):
            self.send('Error: Your name must only contain letters, numbers, and no spaces. Please retry.')

        # Make sure the nickname isn't already use
        elif nickname in [user.nickname for user in self.instances]:
            self.send('Error: This name is already taken. Please choose another one.')

        else:
            old_nickname = self.format_nick
            self.nickname = nickname
            self.refresh_format_nick()
            self.send('Your nickname is now ' + self.format_nick + '.')
            self.send_channels(old_nickname + ' changed its name to ' + self.format_nick + '.', to_self = False)

    def refresh_format_nick(self):
        if self.superadmin:
            self.format_nick = COLOR_SUPERADMIN + self.nickname + COLOR_SYS
        elif self in self.current.admins:
            self.format_nick = COLOR_ADMIN + self.nickname + COLOR_SYS
        else:
            self.format_nick = COLOR_DEFAULT + self.nickname + COLOR_SYS

    def kick(self, nick):
        for user in self.current.members:
            if user.nickname == nick:
                if not user.superadmin:
                    # If the user is not on the MAIN channel, make it leave the current channel and switch to MAIN channel instead.
                    channel = self.find_channel('MAIN')
                    if user.current != channel:
                        user.send('You have been kicked from ' + user.current.name + ' by ' + self.format_nick + '.')
                        old_channel = user.current
                        user.switch(channel)
                        
                        # Remove the user from the previous channel
                        if user in old_channel.members: old_channel.members.remove(user)
                        if user in old_channel.admins: old_channel.admins.remove(user)
                    
                    else:
                        if self.superadmin:
                            self.send(user.format_nick + ' cannot be kicked because it is already on channel "Main".\nMaybe try the command /TIMEOUT or /BAN instead.')
                        else:
                            self.send(user.format_nick + ' cannot be kicked because it is already on channel "Main".\nMaybe ask a SuperAdmin for help.')
                    return
                else:
                    self.send('You are not allowed to kick a SuperAdmin!')
                    return
        user.send(nick + ' is not currently connected or not on this channel.')
        

    def recv(self):
        return self.sock.recv(buffer_size).decode('utf8')
    
    def send(self, msg, sys = True):
        if sys: msg = COLOR_SYS + msg + '\n' + COLOR_DEFAULT
        try:
            self.sock.send(bytes(msg + '\n', 'utf8'))
        except Exception:
            del_user(self)    

    def send_channel(self, msg, sys = True, to_self = True, to_non_currents_only = False, to_currents_only = False):
        for user in self.current.members:
            if to_non_currents_only and user.current != self.current:
                user.send(msg, sys)
            elif to_currents_only and user.current == self.current:
                user.send(msg, sys)
            elif not to_non_currents_only and not to_currents_only:
                user.send(msg, sys)             

    def send_channels(self, msg, sys = True, to_self = True, to_current = True, to_MAIN = True):
        sender_channels = []
        for channel in self.channels:
            if self in channel.members:
                if (channel != self.current or to_current) and (channel.name != 'MAIN' or to_MAIN):
                    sender_channels += [channel]
        for user in self.instances:
            if user.current in sender_channels:
                if user.nickname != self.nickname or to_self:
                    user.send(msg, sys)

    def send_all(self, msg, sys = True, to_self = True):
        for user in self.instances:
            if user.nickname != self.nickname or to_self:
                user.send(msg, sys)
        




def del_user(user):
    '''Used to delete a outgoing user. Delete it from everywhere before closing the connection.'''
    user.send_channels(user.format_nick + ' has left the chat.', to_self = False)
    for channel in user.channels:
        if user in channel.members: channel.members.remove(user)
        if user in channel.admins: channel.admins.remove(user)
    user.sock.close()
    if user in user.instances: user.instances.remove(user)


def accept_incoming_connections():
    '''Sets up handling for incoming clients.'''
    
    while True:
        client, client_address = server.accept()
        user = User(client, client_address)
        if user.address not in user.banned:
            print(user.address + ' has connected.')
            Thread(target=handle_user, args=(user,)).start()
        else:
            print(user.address + ' tried to connect, but it is banned.')
            user.send('You are ban from this server.')
            del_user(user)


def handle_user(user):
    '''Handles a single user.'''

    if len(user.instances) == 1:
        user.superadmin = True
        user.send('Welcome, you are the first connected on the chat.\nThus, by the rules of this kingdom,\nyou shall be granted the title of ' + COLOR_SUPERADMIN + 'SuperAdmin.' + COLOR_SYS)
        user.send('Please, allow me to ask for your name, Your Majesty...')
    else:
        user.send('Welcome! Please type your name and then press enter!')

    # Continue to ask if the nickname proposed isn't acceptable.
    while user.nickname == None:

        # If the connection has been lost, properly kill delete the user and stop the loop.
        try: proposed_name = user.recv()
        except Exception:
            print(user.address + ' was forcibly closed by the remote host.')
            del_user(user)
            return
        
        user.change_nick(proposed_name)

    user.send('Welcome ' + user.format_nick + '! You can type /HELP to display all available commands.')
    user.current.members.remove(user)

    # Add the user to MAIN
    channel = user.find_channel('MAIN')
    channel.members += [user]
    if user.superadmin: channel.admins += [user]
    user.switch(channel)

    # The main loop. While the connection is established
    while True:

        # If the connection has been lost, properly kill delete the user and stop the loop.
        try: msg = user.recv()
        except Exception:
            print(user.address + ' was forcibly closed by the remote host.')
            del_user(user)
            break

        # We have received a message from the user. Let's handle every command he might use.
        
        if msg == '[COMMAND] HELP':
            tmp =  'SuperAdmins have a ' + COLOR_SUPERADMIN + 'magenta name' + COLOR_SYS
            tmp += ', admins have a ' + COLOR_ADMIN + 'red name' + COLOR_SYS + ', private message are ' + STYLE_DIM + 'shown dimmed.\n'+ STYLE_DIM_RESET
            tmp += 'Here is the list of all available commands:\n'
            tmp += ' - /HELP: print this message.\n'
            tmp += ' - <message>: send a message in current channel.\n'
            tmp += ' - /LIST: list all available channels on server.\n'
            tmp += ' - /JOIN <channel>: join (or create) a channel.\n'
            tmp += ' - /LEAVE: leave current channel.\n'
            tmp += ' - /WHO: list users in current channel.\n'
            tmp += ' - /MSG <nick1;nick2;...> <message>: send a private message to user(s) in the current channel.\n'
            tmp += ' - /BYE: disconnect from server.\n'
            tmp += ' - /CURRENT: print the current channel, and the channel you are member of.\n'
            tmp += ' - /CURRENT <channel>: set current channel.\n'
            tmp += ' - /NICK <nick>: change user nickname on server.\n'
            
            if user in user.current.admins:
                tmp += '\nAdmins have also access to the following commands:.\n'
                tmp += ' - /KICK <nick>: kick user from current channel.\n'
                tmp += ' - /REN <channel>: change the current channel name.\n'
                tmp += ' - /GRANT <nick>: grant admin privileges to a user.\n'
                tmp += ' - /REVOKE <nick>: revoke admin privileges.\n'

            if user.superadmin:
                tmp += '\nSuperAdmins have also access to the following commands:\n'
                tmp += ' - /SHOUT <message>: send a public message to everyone, regardless of the channel.\n'
                tmp += ' - /BAN <nick>: forbid a IP adress to connect to the server.\n'
            else:
                tmp += '\nYou will need the help of a SuperAdmin to ban a disrespectful user.\n'

            user.send(tmp)


        elif msg == '[COMMAND] LIST':
            tmp = 'Here are all available channels:\n'
            for channel in user.channels:
                if channel.name != 'VOID': tmp += ' - ' + channel.name + '\n'
            user.send(tmp)

        elif msg[:len('[COMMAND] JOIN ')] == '[COMMAND] JOIN ':
            desired_channel = msg[len('[COMMAND] JOIN '):]
            channel = user.find_channel(desired_channel)


            
            # If channel doesn't exist, create it and become admin of this channel
            if channel == None:
                # Except if the name is invalid
                if not bool(match('^[a-zA-Z0-9]+$', desired_channel)):
                    user.send('Error: A channel\'s name must only contain letters, numbers, and no spaces. Please retry.')
                else: 
                    new_channel = Channel(desired_channel)
                    user.channels += [new_channel]
                    new_channel.members += [user]
                    new_channel.admins += [user]
                    user.switch(new_channel)
                    
            # Forbid user to go to VOID
            elif channel.name == 'VOID':
                self.send('Error: This channel cannot be accessed. Please try something else.')
                
            # If the user isn't part of the channel, it joins it
            elif user not in channel.members:
                channel.members += [user]
                # Add the superadmins in the desired channel admins if it's not already the case
                if user.superadmin and user not in channel.admins: channel.admins += [user]
                user.switch(channel)
                
            else:
                user.send('Error: You already joined this channel. Use /CURRENT ' + channel.name + ', to change your current channel.')

            
        elif msg == '[COMMAND] LEAVE':
            if user.current.name != 'MAIN':
                old_channel = user.current
                user.send_channel(user.format_nick + ' has left the channel.', to_self = False, to_currents_only = True)
                user.switch(user.find_channel('MAIN'))

                # Remove the user from the previous channel
                if user in old_channel.members: old_channel.members.remove(user)
                if user in old_channel.admins: old_channel.admins.remove(user)
                
                # If there is not longer any member in the old channel, remove the channel.
                if len(old_channel.members) == 0: user.channels.remove(old_channel)
            else:
                user.send('You cannot leave while being in the MAIN channel. If you wish to leave, use the command /BYE.')

        elif msg == '[COMMAND] WHO':
            tmp = 'Here are all users in "' + user.current.name + '":\n'
            for client in user.current.members:
                tmp += ' - ' + client.format_nick + '\n'
            user.send(tmp)

        elif msg[:len('[COMMAND] MSG ')] == '[COMMAND] MSG ':
            tmp = msg[len('[COMMAND] MSG '):]

            # Separate all the different recipients included in the command.
            user_to_send = []
            index = tmp.find(';')
            
            while index != -1:
                user_to_send += [tmp[:index]]
                tmp = tmp[index + 1:]
                index = tmp.find(';')

            index = tmp.find(' ')
            if index == -1:
                user.send('Error: Improper usage of the command MSG.\n* /MSG <nick1;nick2;...> <message>: send a private message to one or several user(s) in current channel')
            else:
                user_to_send += [tmp[:index]]
                tmp = tmp[index + 1:]

                # Once done, send the message to all of them, using a different appearence to differentiate them from normal messages.
                for e in user_to_send:
                    result = user.find_user(e)
                    if result != None:
                        user.send(STYLE_DIM + 'To ' + result.format_nick + COLOR_DEFAULT + ': ' + tmp + STYLE_DIM_RESET, sys = False)
                        result.send(STYLE_DIM + 'From ' + user.format_nick + COLOR_DEFAULT + ': ' + tmp + STYLE_DIM_RESET, sys = False)
                    else:
                        user.send(e + ' is not currently connected or is not in your current channel.')

        elif msg == '[COMMAND] BYE':
            print(user.address + ' has left.')
            user.send('Goodbye ' + user.format_nick + '!')
            del_user(user)
            break

        elif msg == '[COMMAND] CURRENT':
            tmp =  'You are currently in the channel "' + user.current.name + '".\n'
            tmp += 'You are also member of the following channels:\n'
            for channel in user.channels:
                if user in channel.members and channel.name != user.current.name:
                    tmp += ' - ' + channel.name + '\n'
            user.send(tmp)

        elif msg[:len('[COMMAND] CURRENT ')] == '[COMMAND] CURRENT ':
            desired_channel = msg[len('[COMMAND] CURRENT '):]
            tmp = user.find_channel(desired_channel)
            
            if tmp != None:
                if user in tmp.members:
                    if user.current != tmp:
                        user.switch(tmp)
                    else:
                        user.send('Error: You are already in this channel.')
                else:
                    user.send('Error: You are not member of this channel. Use /JOIN ' + tmp.name + ', to joint this channel.')
            else:
                user.send('Error: This channel does not exists. You can create it using the command /JOIN ' + desired_channel)

        elif msg[:len('[COMMAND] NICK ')] == '[COMMAND] NICK ':
            desired_nickname = msg[len('[COMMAND] NICK '):]
            user.change_nick(desired_nickname)
                
        elif msg[:len('[COMMAND] GRANT ')] == '[COMMAND] GRANT ':
            desired_admin = msg[len('[COMMAND] GRANT '):]
            if user in user.current.admins:
                result = user.find_user(desired_admin)
                if result != None:
                    if result not in result.current.admins:
                        result.current.admins += [result]
                        result.refresh_format_nick()
                        result.send(user.format_nick + ' granted you the Admin title!')
                        result.send_channel(result.format_nick + ' is now Admin.', to_self = False)
                    else:
                        user.send(desired_admin + ' is already Admin.')
                else:
                    user.send(desired_admin + ' is not currently connected or is not in your current channel.')
            else:
                user.send('You are not allowed to use this command!')

        elif msg[:len('[COMMAND] REVOKE ')] == '[COMMAND] REVOKE ':
            desired_admin = msg[len('[COMMAND] REVOKE '):]
            if user in user.current.admins:
                result = user.find_user(desired_admin)
                if result != None:
                    if result in result.current.admins:
                        if not result.superadmin:
                            result.current.admins.remove(result)
                            result.refresh_format_nick()
                            result.send(user.format_nick + ' revoked your Admin title!')
                            result.send_channel(result.format_nick + ' is no longer an Admin.', to_self = False)
                        else:
                            user.send('You are not allowed to revoke a SuperAdmin!')
                    else:
                        user.send(desired_admin + ' is not an Admin.')
                else:
                    user.send(desired_admin + ' is not currently connected or is not in your current channel.')
            else:
                user.send('You are not allowed to use this command!')

        elif msg[:len('[COMMAND] KICK ')] == '[COMMAND] KICK ':
            desired_nickname = msg[len('[COMMAND] KICK '):]
            if user in user.current.admins:
                user.kick(desired_nickname)
            else:
                user.send('You are not allowed to use this command!')

        elif msg[:len('[COMMAND] REN ')] == '[COMMAND] REN ':
            desired_name = msg[len('[COMMAND] REN '):]
            if user in user.current.admins:
                if user.current.name != 'MAIN':
                    user.send_channel('This channel is now called ' + user.current.name, to_currents_only = True)
                    user.send_channel('The channel ' + user.current.name + ' is now called ' + user.current.name, to_non_currents_only = True)
                    user.current.name = desired_name
                else:
                    user.send('You cannot change the channel "MAIN" name.\nSorry, even admin\'s powers have limits.') 
            else:
                user.send('You are not allowed to use this command!') 

        elif msg[:len('[COMMAND] SHOUT ')] == '[COMMAND] SHOUT ':
            desired_msg = msg[len('[COMMAND] SHOUT '):]
            if user.superadmin:
                user.send_all('\n\n' + desired_msg)
            else:
                user.send('You are not allowed to use this command!') 

        elif msg[:len('[COMMAND] BAN ')] == '[COMMAND] BAN ':
            desired_user = msg[len('[COMMAND] BAN '):]
            if user.superadmin:
                result = user.find_user(desired_user)
                if result != None:
                    result.send('You have been banned from this server by ' + user.format_nick + '!')
                    user.send_all(result.format_nick + ' has been banned from this server')
                    user.banned += [result.address]
                    del_user(result)
                    
                else:
                    user.send(desired_admin + ' is not currently connected or is not in your current channel.')
            else:
                user.send('You are not allowed to use this command!')

        elif msg[:len('[COMMAND] ')] == '[COMMAND] ':
            user.send('The command /' + msg[len('[COMMAND] '):] + ' is not recognized.\nYou can type /HELP to display all available commands.')


        # If the message isn't a command, it must be a normal message. Sends it to everyone on all the channels the user has joined.
        else:
            user.send_channel(user.format_nick + COLOR_DEFAULT + ': ' + msg, sys = False, to_currents_only = True)
            user.send_channel('[' + user.current.name + '] ' + user.format_nick + COLOR_DEFAULT + ': ' + msg, sys = False, to_non_currents_only = True)




host = ''
port = 1459
buffer_size = 1500

server = socket(AF_INET, SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server.bind((host, port))

server.listen(10)

print('The server has succefully launched. Now waiting for client connection...')
thread = Thread(target=accept_incoming_connections)
thread.start()
thread.join()
server.close()
