#include "host.h"
#define SINT_2_UINT(a) ((a+32768)*255/65535)
Host::Host()
{
    this->broadCastSock = new QUdpSocket();;
    this->commSock = new  QUdpSocket();
    this->commSock->bind(HOST_LISTENING_PORT);
    //this->gameData = new GameData();
}
Host::~Host()
{

}
void Host::sendBroadcast()
{
    QByteArray datagram;
    QList<QHostAddress> data = QNetworkInterface::allAddresses();
    foreach (const QHostAddress &address, QNetworkInterface::allAddresses()) //send a broadcast on all network connections
    {
        //check that connection is not a loopback and supports our protcol
        if (address.protocol() == QAbstractSocket::IPv4Protocol && (address != QHostAddress(QHostAddress::LocalHost)))
        {
             datagram.append(address.toString().toLocal8Bit()); //write connection ip to datagram
             this->broadCastSock->writeDatagram(datagram, QHostAddress::Broadcast, BROADCAST_PORT); //broadcast datagram
             datagram.clear(); //clear the datagram for the next iteration
        }
    }
}

void Host::sendGameSync(QByteArray dgram)
{
    // for(int i = 0;i<this->clients->size();i++)
    // {
    //     this->commSock->writeDatagram(dgram,this->clients->at(i).addr,this->clients->at(i).port);
    // }
}

void Host::readData()
{
    QByteArray datagram;
    datagram.resize(this->commSock->pendingDatagramSize());
    QHostAddress sender;
    quint16 senderPort;

    this->commSock->readDatagram(datagram.data(), datagram.size(),&sender, &senderPort);
    D_MSG(datagram.data());
    this->checkValidDgram(datagram,sender,senderPort);
}

bool Host::checkValidDgram(QByteArray dgram, QHostAddress sender, quint16 senderPort)
{
    return true;
}

void Host::parseDgram(QByteArray dgram)
{
    // QString header = QString::fromUtf8(dgram.data()).section("#",0,0);
    // QStringList allData = QString::fromUtf8(dgram.data()).section("#",1,1).split(";");
    // for(int i =0;i<allData.size();i++)
    // {
    //     QStringList playerInfo = allData.at(i).split(":");
    //     int index = playerInfo.at(0).at(1).digitValue()-1;
    //     QString name = playerInfo.at(1);
    //     JoystickData data;
    //     data.lX = qint16(playerInfo.at(4).toInt());
    //     data.lY = qint16(playerInfo.at(5).toInt());
    //     data.rX = qint16(playerInfo.at(6).toInt());
    //     data.rY = qint16(playerInfo.at(7).toInt());
    //     data.lT = qint16(playerInfo.at(8).toInt());
    //     data.rT = qint16(playerInfo.at(9).toInt());
    //     data.buttons.bttns = quint16(playerInfo.at(10).toInt());
    // }

}
void Host::sendRobotSync()
{
}


