#ifndef BROADCAST_H
#define BROADCAST_H

#include <QObject>
#include <QtNetwork>
#include <joystickhandler.h>

#define BROADCAST_PORT 2367
#define HOST_LISTENING_PORT 2367

#define DEBUG /* comment out this line to lower the verbosity of the program */


#if  defined(DEBUG) || defined(GLOBAL_DEBUG)
#define D_MSG(a) qDebug()<<a
#else
#define D_MSG(a)
#endif

typedef struct{
    QHostAddress addr;
    qint16 port;
    QString name;
}ConnectedClient;
typedef struct{
    QHostAddress addr;
    qint16 port;
    QString name;
}ConnectedRobot;
class Host : QObject
{
    Q_OBJECT
public:
    Host();
    ~Host();

public slots:
    void sendBroadcast();
    void sendGameSync(QByteArray dgram);
    void readData();
    bool checkValidDgram(QByteArray dgram,QHostAddress sender, quint16 senderPort);
    void parseDgram(QByteArray dgram);
    void sendRobotSync();
signals:
    void receivedValidDgram(QByteArray dgram);
    void newClient(QByteArray dgram);
    void receivedDbgMsg(QByteArray dgram);
    void clientAdded();
    void robotAdded();
private:
    QUdpSocket *broadCastSock;
    QUdpSocket *commSock;
    QHostAddress multiAddr;
};


#endif // BROADCAST_H
