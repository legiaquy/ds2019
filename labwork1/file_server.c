#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

int main(){
int sockid, cli, pid;
struct sockaddr_in ad;
char s[50];
socklen_t ad_length = sizeof(ad);

// INIT SOCKET
sockid = socket(AF_INET, SOCK_STREAM, 0);

// BIND SOCKET TO port 2509
memset(&ad, 0, sizeof(ad));
ad.sin_family = AF_INET;
ad.sin_addr.s_addr = INADDR_ANY;
ad.sin_port = htons(2509);
bind(sockid, (struct sockaddr *)&ad, ad_length);

// LISTEN TO CLIENT(S)

listen(sockid, 0);
printf("Listening...\n");
while (1) {
	// ACCEPT CLIENT(S)
	cli = accept(sockid, (struct sockaddr *)&ad, &ad_length);
	pid = fork();
	if (pid == 0) {
		printf("cilent connected\n");
		while(1) {
			// RECEIVE/SEND MESSAGES
			read(cli, s, sizeof(s));
			printf("client says: %s\n",s);

			printf("server>", s);
			scanf("%s", s);
			write(cli, s, strlen(s) + 1);
		}
		return 0;
	} else {
		// accept more clients
		continue;
	}
}

// FINISHED SOCKET
close(cli);
printf("End chat!\n");

}
