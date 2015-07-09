#include "SocketManager.hpp"
#include "Socket.hpp"
#include "TimerManager.hpp"
#include "Exceptions.hpp"
#include "ErrorStrings.hpp"

#include <winsock2.h>
#include <windows.h>

using namespace std;


void SocketManager::check ( uint64_t timeout )
{
    if ( ! initialized )
        return;

    if ( changed )
    {
        for ( Socket *socket : allocatedSockets )
        {
            if ( activeSockets.find ( socket ) != activeSockets.end() )
                continue;

            LOG_SOCKET ( socket, "added" );
            activeSockets.insert ( socket );
        }

        for ( auto it = activeSockets.cbegin(); it != activeSockets.cend(); )
        {
            if ( allocatedSockets.find ( *it ) != allocatedSockets.end() )
            {
                ++it;
                continue;
            }

            LOG ( "socket=%08x removed", *it ); // Don't log any extra data cus already deleted
            activeSockets.erase ( it++ );
        }

        changed = false;
    }

    if ( activeSockets.empty() )
        return;

    fd_set readFds, writeFds;
    FD_ZERO ( &readFds );
    FD_ZERO ( &writeFds );

    for ( Socket *socket : activeSockets )
    {
        if ( socket->isConnecting() && socket->isTCP() )
            FD_SET ( socket->fd, &writeFds );
        else
            FD_SET ( socket->fd, &readFds );
    }

    ASSERT ( timeout > 0 );

    timeval tv;
    tv.tv_sec = timeout / 1000UL;
    tv.tv_usec = ( timeout * 1000UL ) % 1000000UL;

    // Note: select should be called between timeBeginPeriod / timeEndPeriod to ensure accurate timeouts
    int count = select ( 0, &readFds, &writeFds, 0, &tv );

    if ( count == SOCKET_ERROR )
        THROW_WIN_EXCEPTION ( WSAGetLastError(), "select failed", ERROR_NETWORK_GENERIC );

    if ( count == 0 )
        return;

    ASSERT ( TimerManager::get().isInitialized() == true );
    TimerManager::get().updateNow();

    for ( Socket *socket : activeSockets )
    {
        if ( allocatedSockets.find ( socket ) == allocatedSockets.end() )
            continue;

        if ( socket->isConnecting() && socket->isTCP() )
        {
            if ( ! FD_ISSET ( socket->fd, &writeFds ) )
                continue;

            LOG_SOCKET ( socket, "socketConnected" );
            socket->socketConnected();
        }
        else
        {
            if ( ! FD_ISSET ( socket->fd, &readFds ) )
                continue;

            if ( socket->isServer() && socket->isTCP() )
            {
                LOG_SOCKET ( socket, "socketAccepted" );
                socket->socketAccepted();
            }
            else
            {
                LOG_SOCKET ( socket, "socketRead" );
                socket->socketRead();
            }
        }
    }
}

void SocketManager::add ( Socket *socket )
{
    LOG_SOCKET ( socket, "Adding socket" );
    allocatedSockets.insert ( socket );
    changed = true;
}

void SocketManager::remove ( Socket *socket )
{
    if ( allocatedSockets.erase ( socket ) )
    {
        LOG_SOCKET ( socket, "Removing socket" );
        changed = true;
    }
}

void SocketManager::clear()
{
    LOG ( "Clearing sockets" );
    for ( auto it = allocatedSockets.begin(); it != allocatedSockets.end(); )
        ( *it++ )->disconnect();
    activeSockets.clear();
    allocatedSockets.clear();
    changed = true;
}

SocketManager::SocketManager() {}

void SocketManager::initialize()
{
    if ( initialized )
        return;

    initialized = true;

    // Initialize WinSock
    WSADATA wsaData;
    int error = WSAStartup ( MAKEWORD ( 2, 2 ), &wsaData );

    if ( error != NO_ERROR )
        THROW_WIN_EXCEPTION ( error, "WSAStartup failed", ERROR_NETWORK_INIT );
}

void SocketManager::deinitialize()
{
    if ( ! initialized )
        return;

    initialized = false;

    SocketManager::get().clear();

    WSACleanup();
}

SocketManager& SocketManager::get()
{
    static SocketManager instance;
    return instance;
}
