#!/bin/bash

# Funzione per installare Tor
install_tor() {
    echo "Installing Tor using Homebrew..."
    brew install tor
}

# Funzione per avviare il servizio Tor
start_tor() {
    echo "Starting Tor service..."
    brew services start tor
}

# Funzione per fermare il servizio Tor
stop_tor() {
    echo "Stopping Tor service..."
    brew services stop tor
}

restart_tor() {
    echo "Restarting Tor service..."
    brew services restart tor
}

# Funzione per verificare lo stato del servizio Tor
status_tor() {
    echo "Checking Tor service status..."
    brew services list | grep tor
}

# Funzione per verificare la connessione tramite Tor
test_tor_connection() {
    echo "Testing Tor connection..."
    curl --socks5-hostname 127.0.0.1:9050 http://check.torproject.org
}

# Menu per l'utente
echo "Tor Service Management Script"
echo "=============================="
echo "1. Install Tor"
echo "2. Start Tor service"
echo "3. Restart Tor service"
echo "4. Stop Tor service"
echo "5. Check Tor service status"
echo "6. Test Tor connection"
echo "7. Exit"
echo -n "Please choose an option [1-6]: "

read choice

case $choice in
    1)
        install_tor
        ;;
    2)
        start_tor
        ;;
    3)
        restart_tor
        ;;
    4)
        stop_tor
        ;;
    5)
        status_tor
        ;;
    6)
        test_tor_connection
        ;;
    7)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option, please choose a valid number between 1 and 6."
        ;;
esac
