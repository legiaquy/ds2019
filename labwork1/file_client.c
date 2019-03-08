#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

int main(int argc, char* argv[]){
int sockid, status;
char s[50];
struct sockaddr_in ad;
struct hostent *hep;
socklen_t ad_length = sizeof(ad);

// INIT SOCKET
sockid = socket(AF_INET, SOCK_STREAM, 0);

// BIND TO PORT 2509
hep = gethostbyname(argv[1]);
memset(&ad, 0, sizeof(ad));
ad.sin_family = AF_INET;
ad.sin_port = htons(2509);
ad.sin_addr = *(struct in_addr *)hep->h_addr_list[0];

// CONNECT TO SERVER
connect(sockid, (struct sockaddr *)&ad, ad_length);

while(1) {
// SEND/RECEIVE MESSAGES
printf("cilent>");
scanf("%s", s);
write(sockid, s, strlen(s) + 1);

read(sockid, s, sizeof(s));
printf("server says: %s\n", s);
}

}
