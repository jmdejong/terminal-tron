# Terminal Tron

A multiplayer tron game made for [tilde.town](http://tilde.town)


# Usage
See instructions.txt for the latest usage documentation.
### Server
    usage: hosttron.py [-h] [-s SOCKET]

    optional arguments:
      -h, --help            show this help message and exit
      -s SOCKET, --socket SOCKET
                            The socket file to listen to. This is useful if
                            another server is already using the default socket
                            file or if it wasn't removed properly. WARNING: if the
                            given file exists it will be overwritten. Defaults to
                            /tmp/tron_socket
### Client
    usage: playtron.py [-h] [-n NAME] [-s SOCKET] [-p]

    optional arguments:
      -h, --help            show this help message and exit
      -n NAME, --name NAME  Your player name (must be unique!). Defaults to
                            username
      -s SOCKET, --socket SOCKET
                            The socket file to connect to. Defaults to
                            /tmp/tron_socket
      -p, --spectate        Join as spectator

# Known bugs

The socket file is not removed when the server is killed.
Please do this manually after killing the server.
If anyone happens to know how to do this correctly, please tell me.
