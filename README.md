# IRChat

## Introduction

L’IRChat est un logiciel de communication, basé sur le protocole IRC (RFC1459). Le programme est composé de deux fichiers sources : Le serveur et le client (non interchangeable). Les utilisateurs peuvent discuter sur le canal principal, des canaux secondaires, ou même plusieurs à la fois. Ils peuvent également échanger des messages privés à destination d’un ou plusieurs utilisateurs. Beaucoup d’autres commandes sont à leur disposition (description détaillée dans la partie fonctionnalité). L’interface graphique est très confortable pour un programme fonctionnant dans le terminal. Notez d’ailleurs que seule les terminaux type ANSI / VT100 sont compatibles avec le système graphique utilisé. Pour cette raison, les utilisateurs Windows seront obligés d’utiliser un terminal axillaire (« CMDer » par exemple, inclus dans les fichiers sources de IRChat).

## Protocole réseau

IRChat utilise les fonctionnalités d’échange de donnée en réseau offertes par la librairie de base de Python (module « socket »). Pour se connecter à un serveur, le client à besoin de l’adresse IPv4 du server. Le port utilisé est le port 1459 (comme indiqué dans le cahier des charges). Le serveur gère les transfert réseaux avec les clients dans des sockets uniques. Si l’utilisateur le souhaite, il peut se déconnecter en utilisant le fonction /BYE. Le serveur peut également décider de rejeter ou d’arrêter une communication (pour exemple si l’utilisateur est banni ou que la communication est perdue). De nombreuse commande peuvent être utilisé. Elles sont préfixées d’un / qui n’est pas envoyé sur le réseau ; elles sont remplacées automatiquement par le préfixe « [COMMAND] », à l’envoie par le client. 

## Interface graphique

Afin d’afficher les messages reçus, ainsi que de permettre à l’utilisateur d’en écrire un, le module « sys » à été utilisé. En effet, l’utilisation d’un « basique » input n’aurait pas permet à 
Thomas BARILLOT 21727699 INF401A5 
l’utilisateur de recevoir d’information pendant l’écriture de son propre message ; input bloque la progression du programme jusqu’à ce que l’utilisateur presse la touche « Entrée ». De ce fait, l’utilisation de sys.stdin.readline() a été nécessaire. Il est également bon d’indiquer que l’intégralité du programme, les commentaires ainsi que l’interfaces utilisateur sont entièrement écrits en anglais. Afin de personnaliser l’interface terminal de l’utilisateur, des codes ANSI spéciaux ont été utilisé (appelé les « ANSI Escape Sequences »). Ceux-ci permettent notamment l’affichage de couleur différente dans le terminal, d’effacer des lignes ou d’effacer l’intégralité de l’écran. Ainsi, lorsque l’utilisateur lance le programme, l’interface terminal est effacée, ne laissant place qu’au message d’accueil du serveur. Dans l’éventualité où les informations de connexion par défaut ne fonctionnent pas, il est proposé à l’utilisateur de modifier les paramètres de connexion : 
 
 
![](https://www.r-entries.com/etuliens/img/IRC/image1.png)
 
 
Répondre « non » clôture le programme. « Oui » permet de réessayer avec de nouveaux paramètres. 
 
![](https://www.r-entries.com/etuliens/img/IRC/image2.png) 

Ci-dessus, l’utilisateur vient de se connecter au serveur. Etant le premier utilisateur connecté, il est promu au rang de SuperAdmin. Ce type d’utilisateur à des droits supplémentaires qui seront décrient en plus grand détails dans la partie fonctionnalité. Ce que l’on peut noter ici c’est que les utilisateurs SuperAdmin se démarque par la couleur magenta. Les utilisateurs suivants verront une autre page, légèrement moins « décalé » mais demmandant toujours d’entrer un pseudonyme.

Afin de ne pas encombré l’écran des message écrit dans le terminal par l’utilisateur, ceux-ci sont supprimé après l’envoie à l’aide des caractères ANSI suivant : 

Ainsi lorsque l’utilisateur écrit un message, celui est instantanement remplacé par la version serveur, tel que les autres utilisateurs verront : 

![](https://www.r-entries.com/etuliens/img/IRC/image3.png) 
![](https://www.r-entries.com/etuliens/img/IRC/image4.png) 

![](https://www.r-entries.com/etuliens/img/IRC/image5.png) 

Ci-dessus, un exemple assez standard de discussion. Vous pouvez notez les couleurs SuperAdmin (magenta) et Admin (rouge), s’applique même des les messages systèmes (aussi appelé Sys dans le programme).

Une des limitations du programme est la capacité au client de conserver le message en cours d’écriture tout en recevant en temps réelle les messages des autres utilisateurs. Ici, l’implémentation est loin d’être parfaite d’un point de vue graphique. Le message en cours d’écriture est visuellement effacé. Cependant il est toujours stocké, mais invisible. Si l’utilisateur continue d’écrire son message sans se soucier de cet incident, il peut ensuite appuyer sur Entrée est envoyé le message comme si de rien n’était. Malgré de nombreux essaie avec les « ANSI Escape Sequences », améliorer ce système paré insurmontable.

## Fonctionnalités

### La commande /HELP
De nombreuses fonctions sont proposées à l’utilisateur. Lors de sa connection, celui-ci sera invité à utiliser la commande /HELP pour en découvrir la liste : 
 
 
 ![](https://www.r-entries.com/etuliens/img/IRC/image6.png)
 
 
 
 
 
 
L’utilisateur ci-dessus étant un SuperAdmin, la liste complète des commandes est affichée. Trois types d’utilisateurs coexistent sur le serveur :
- Les utilisateurs Standard : Couleur blanche
- Les utilisateurs Admin : Couleur rouge. Le titre d’Admin ne s’étend par au-delà d’un chanel unique. Tous utilisateurs peuvent devenir Admin en créant un nouveau chanel. Un utilisateur peut également devenir Admin si un autre Admin (ou SuperAdmin) utilise la fonction /GRANT (« autoriser » en français). Pour finir, un utilisateur peut devenir Admin dans le cas où le dernier Admin d’un chanel se déconnecte et que celui-ci est la personne ayant passé le plus de temps sur le chanel.
- Les utilisateur SuperAdmin : Couleur magenta. Ils peuvent utiliser davantage de commande comme /SHOUT pour envoyer un message public à tous les utilisateurs, quel que soit le chanel, et /BAN pour bannir l’adresse IP d’un utilisateur du serveur. 
 
Informations complémentaires : Les commandes doivent être écrire correctement, en MAJUSCULE, sinon le programme renvoie le message ci-dessous : 

![](https://www.r-entries.com/etuliens/img/IRC/image7.png)
 
### La commande /LIST 
La commande /LIST permet d’afficher l’ensemble des canaux disponibles. « MAIN », le canal principal, est toujours listé car impossible à supprimer. Un autre canal « VOID » est masqué du côté utilisateur mais est présent dans le code du programme. Les utilisateurs venant de se connecter mais n’ayant pas encore écris leur pseudonyme sont connecté sur ce canal. Ils seront après automatiquement transféré sur le canal « MAIN ». 

### La commande /JOIN 
/JOIN permet à la fois de rejoindre un canal existant, ou de créer un nouveau canal. Ainsi « /JOIN Test » créera le canal Test si celui-ci n’existe pas. L’utilisateur est alors automatique transférer à celui-ci et en devient l’administrateur (car il en est le créateur). Notez que l’utilisateur est toujours membres du canal où il se trouvait précédemment, cependant le canal courant a été modifié. Un utilisateur peut être membre de nombreux canaux et avoir des rôles différents dans chacun d’entre eux. Les utilisateurs présents sur un canal sont alertés par l’arrivé ou le départ d’un nouvel utilisateur sur le canal. Ils ne sont pas alertés si l’utilisateur change de canal courant. Les utilisateurs ne peuvent pas rejoindre « VOID », l’accès est interdit. Ils ne peuvent pas non plus rejoindre un canal dont il sont déjà membre, il faut utiliser la commande /CURRENT pour cela. 
 
### Recevoir un message 
Lorsque qu’un utilisateur écrit un message, l’ensemble des personnes connectés au canal reçoivent le message. Il n’est pas possible pour un utilisateur ou Admin d’envoyé un message sur plusieurs canaux. Si l’on reçoit un message sur un canal dont on est membre, mais pas le canal courant, le message est préfixé du nom du canal émetteur, entre crochet : 

![](https://www.r-entries.com/etuliens/img/IRC/image8.png)

### La commande /LEAVE 
La commande /LEAVE permet de quitter le canal courant. L’utilisateur est alors redirigé vers le canal MAIN. C’est d’ailleurs pour cette raison qu’il n’est pas possible de quitter le canal MAIN. L’utilisateur est alors invité à utiliser /BYE s’il souhaite s’en aller. Les utilisateurs encore présents sur le canal seront alertés de l’utilisateur sortant. Si l’utilisateur utilise /LEAVE alors qu’il est Admin du canal, il perdra son titre (sauf pour les SuperAdmin qui sont automatique Admin de n’importe quel chanel). 

### La commande /WHO 
/WHO permet d’afficher l’ensemble des utilisateurs membre du canal courant. Pour connaître l’ensemble des utilisateurs connecté au serveur, il est possible de choisir MAIN comme canal courant, puisque tous les utilisateurs sont membres de MAIN. 

### La commande /MSG 
/MSG permet d’envoyer un message privé à un ou plusieurs utilisateurs membre du canal courant. Celui ou ceux-ci recevront le message, préfixé par « From » (de la part de… en français), afin de les distinguer d’un message normal. Ils sont également légèrement plus foncés sur les terminaux compatibles avec la fonction ANSI DIM. Voici des exemples d’utilisation de la fonction /MSG : /MSG Thomas Salut ! /MSG Thomas;Pierre;Martin Coucou ! Comment ça va ? Notez que lors d’envoi multiple, chaque message est traité séparément. Ainsi, si l’un d’entre eux à pour destinataire un utilisateur inconnu, ou non membre du canal courant, seul celui-ci échouera. L’utilisateur en sera alerté. 

### La commande /BYE 
/BYE permet à l’utilisateur de se déconnecter proprement du serveur. A l’origine, il n’était pas possible de se déconnecter tant que l’utilisateur n’était pas dans le canal principal. Ainsi, s’il était membre d’un canal secondaire, il fallait utiliser la fonction /LEAVE pour revenir au canal MAIN, puis /BYE pour se déconnecter. Cependant, depuis l’extension du programme permettant d’être membre de nombreux réseau, cette limitation a été retiré ; il aurait été trop contraignant de /LEAVE l’ensemble des canaux dont on est membre. Ainsi, /BYE pour être utilisé n’importe où pour quitter le serveur. 

### La commande /CURRENT 
/CURRENT a deux utilisations possibles. Elle peut permettre de connaitre son canal courant (ainsi que les canaux dont on est membre) mais également changer son canal courant. 

![](https://www.r-entries.com/etuliens/img/IRC/image9.png)
![](https://www.r-entries.com/etuliens/img/IRC/image10.png)

### La commande /NICK 
/NICK permet à n’importe quel utilisateur de modifier son pseudonyme. Un pseudonyme est unique à chaque utilisateur est doit alphanumérique, sans espaces ou caractère spéciaux. Cette règle s’applique également au nom du canaux. Lorsque qu’un utilisateur modifie son nom, l’ensemble des utilisateurs membres du canal sont alerté : 
 
 ![](https://www.r-entries.com/etuliens/img/IRC/image11.png)
 
 
### La commande KICK (Admin et SuperAdmin) 
Cette commande permet de forcer un /LEAVE sur un utilisateur. Ainsi, celui-ci est retiré du canal courant. Il faut être dans le même canal que lui pour faire cette opération. Les autres membres et l’utilisateur en question sont alertés : 
 
 ![](https://www.r-entries.com/etuliens/img/IRC/image12.png)
 
Pour les mêmes raisons qu’il n’est pas possible de /LEAVE le canal MAIN, il n’est pas possible de KICK un utilisateur dans MAIN. Il faudra alors se tourner vers les SuperAdmins pour /BAN l’utilisateur. 


### La commande /REN (Admin et SuperAdmin) 
Permet de renommer le canal. Tous les membres en sont alertés : 
 
 ![](https://www.r-entries.com/etuliens/img/IRC/image13.png)
 

### Les commandes /GRANT et /REVOKE (Admin et SuperAdmin) 
/GRANT permet à un Admin ou SuperAdmin de promouvoir un utilisateur standard au rang d’Admin. /REVOKE permet de faire l’opération inverse. 

### La commande /SHOUT (SuperAdmin) 
Cette commande permet aux SuperAdmins d’informer l’ensemble des utilisateurs d’une information importante. Par exemple la fermeture imminente du serveur :  
 
 ![](https://www.r-entries.com/etuliens/img/IRC/image14.png)
 
 
### La commande /BAN (SuperAdmin) 
/BAN permet aux SuperAdmins de déconnecter un utilisateur et d’empêcher sa reconnexion. Son IP est en effet bloquée par le serveur. L’utilisateur essayant de se reconnecter sera alerté qu’il est bel et bien bannis. 
 
### Choix technique : Utiliser des Threads 
Très tôt dans le développement, l’utilisation des Thread (module « threading ») est apparu comme une évidence. Cela permet de facilement paralléliser les opérations : en termes de code, c’est comme si le server n’avait qu’un client à se soucier. Cela permet également une meilleure utilisation des processeurs multicœurs (dans l’éventualité où ce logiciel tourne sur un serveur possédant 4 Xeon de 64 cœurs chacun ^^). 
Mais la dernière raison est vraiment la plus importante. Grâce à la séparation des connections en plusieurs Thread totalement indépendant, si jamais l’utilisateur produit une erreur niveau serveur, seul celui-ci en sera touché ; les autres utilisateurs ne le remarqueront même pas. 
 
 ![](https://www.r-entries.com/etuliens/img/IRC/image15.png)
 
Ci-dessus, on peut voir le serveur accepter des connections, puis une erreur dans Thread-2, puis à nouveau d’autre utilisateur, quittant ou revenant sur le serveur. Si l’utilisateur ayant fait planter son Thread correspondant n’aura qu’à quitter le programme et le relancé pour retrouver une nouvelle connexion sur un nouveau thread. 
 
 
### La console Server 
L’affiche de la console est assez limitée : Nous somme informer d’un utilisateur se connectant, se déconnectant, se déconnectant de manière imprévue et d’une tentative de connexion d’un utilisateur banni.

## Amélioration possible
Parmi les idées qui n’ont pas été implémenté : 
 
- Permettre aux Admins de choisir la couleur d’un canal.
- Transférer des fichiers
- La commande /TIMEOUT <duration> qui permettrait de bloquer les actions d’un utilisateur pendant une durée en minutes. Il pourrait être spectateur et lire les messages sur le canal courant mais pas utiliser de commande ou écrire de message.
- Ajouter un compte Server qui serait SuperAdmin. Il pourrait écrire depuis la console server et aurait un pseudonyme « Server ». Il serait le seul à pouvoir promouvoir de nouveau membre SuperAdmin.
- Améliorer le système d’écrire pour pouvoir voir le message en cours d’écrire pendant que l’on reçoit un autre message (bug graphique expliqué dans « Interfaces Graphique »)
- Ajouter une sorte de « Radio » permettant au serveur d’envoyé des messages à rythme régulier : L’heure, ou alors juste un message de remerciement pour utiliser le serveur avec lien viens un site web par exemple. 
