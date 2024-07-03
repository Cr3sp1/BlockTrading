pragma solidity 0.5.17;

import "./IToken.sol";
import "./IChallenge.sol";

// Dichiarazione del contratto Challenge che implementa l'interfaccia IChallenge
contract Challenge is IChallenge {

    // Struttura dati per rappresentare una singola sfida
    struct ChallengeData {
        uint256 start;
        address challenger;
        address[] rivals;
        bool winnerOne;
        bool winnerTwo;
        address winner;
    }

    // Dichiarazione delle variabili di stato
    uint256 public count_index;
    address private paycoin; // Indirizzo del contratto Paycoin
    uint256 private exp = 10**18; // Valore decimale per le operazioni di calcolo
    ChallengeData[] public challenges; // Mappatura delle sfide per indirizzo
    mapping(address => uint256) private single_challenges; // Mappatura delle sfide singole per indirizzo
    mapping(address => uint256) private team_challenges; // Mappatura delle sfide di squadra per indirizzo
    mapping(uint256 => mapping(address => bool)) private attempts; // Mappatura degli attempt per ogni sfida

    // orari
    uint256 private open_day_1 = 1719471300;
    uint256 private close_day_1 = open_day_1 + 9 hours;
    uint256 private open_day_2 = open_day_1 + 24 hours;
    uint256 private close_day_2 = open_day_2 + 9 hours;
    uint256 private open_day_3 = open_day_2 + 24 hours;
    uint256 private close_day_3 = open_day_3 + 9 hours;
    uint256 private open_day_4 = open_day_3 + 48 hours;
    uint256 private close_day_4 = open_day_4 + 9 hours;
    uint256 private open_day_5 = open_day_4 + 24 hours;
    uint256 private close_day_5 = open_day_5 + 9 hours;

    // Dichiarazione degli eventi
    event One_vs_One(address indexed challenger, address indexed rival, uint256 index); // Evento per sfida uno contro uno
    event One_vs_Two(address indexed challenger, address indexed rival_1, address indexed rival_2, uint256 index); // Evento per sfida uno contro due
    event Win_One(address indexed winner, uint256 reward); // Evento per la vittoria della sfida uno contro uno
    event Win_Two(address indexed winner, uint256 reward); // Evento per la vittoria della sfida uno contro due

    modifier Open(){
        /*require((block.timestamp > open_day_1 && block.timestamp < close_day_1) ||
                (block.timestamp > open_day_2 && block.timestamp < close_day_2) ||
                (block.timestamp > open_day_3 && block.timestamp < close_day_3) ||
                (block.timestamp > open_day_4 && block.timestamp < close_day_4) ||
                (block.timestamp > open_day_5 && block.timestamp < close_day_5)," Marketplace is closed!");*/
                _;
    }


    // Costruttore del contratto
    constructor(address _paycoin) public {
        paycoin = _paycoin; // Inizializza l'indirizzo del contratto Paycoin
    }

    // Funzione per avviare una sfida uno contro uno
    function one_vs_one(address _rival) public Open {
        require(single_challenges[msg.sender] < 10, "Too many challenges"); // Controlla se il numero di sfide è inferiore a 10
        single_challenges[msg.sender] += 1;                                 // Incrementa il numero di sfide singole per l'indirizzo del mittente
        count_index +=1 ;
        address[] memory rivals = new address[](1);
        rivals[0] = _rival;
        challenges.push(ChallengeData({
            start: block.timestamp,
            challenger: msg.sender,
            rivals: rivals,
            winnerOne: true,
            winnerTwo: false,
            winner: address(0)
        }));
        IToken(paycoin).minting(msg.sender, 1000 * exp); // Mint di Paycoin per il mittente
        emit One_vs_One(msg.sender, _rival, count_index - 1); // Emette l'evento One_vs_One
    }

    // Funzione per avviare una sfida uno contro due
    function one_vs_two(address _rival_1, address _rival_2) public Open {
        require(team_challenges[msg.sender] < 10, "Too many challenges"); // Controlla se il numero di sfide di squadra è inferiore a 10
        team_challenges[msg.sender] += 1; // Incrementa il numero di sfide di squadra per l'indirizzo del mittente
        count_index += 1;
        address[] memory rivals = new address[](2);
        rivals[0] = _rival_1;
        rivals[1] = _rival_2;
        challenges.push(ChallengeData({
            start: block.timestamp,
            challenger: msg.sender,
            rivals: rivals,
            winnerOne: false,
            winnerTwo: true,
            winner: address(0)
        }));
        IToken(paycoin).minting(msg.sender, 2000 * exp); // Mint di Paycoin per il mittente
        emit One_vs_Two(msg.sender, _rival_1, _rival_2, count_index - 1); // Emette l'evento One_vs_Two
    }

    // TODO change require with if + return message (otherwise transaction reverted)

    // Funzione per dichiarare la vittoria in una sfida uno contro uno
    function win_one(uint256 challengeIndex) public Open returns (bool) {
        require( challengeIndex < count_index, "Challenge index not valid.");
        require(!attempts[challengeIndex][msg.sender], "Attempt already made"); // NO SPAM
        attempts[challengeIndex][msg.sender] = true; // NO SPAM
        ChallengeData storage challenge = challenges[challengeIndex];
        require(msg.sender == challenge.challenger || msg.sender == challenge.rivals[0], "Permission denied"); // Controlla se il mittente è il sfidante o il rivale
        require(challenge.winnerOne, "Too late");
        if( block.timestamp >= challenge.start + 20 seconds ){
            challenge.winnerOne = false; // Resetta lo stato della sfida
            challenge.winner = msg.sender;
            IToken(paycoin).minting(msg.sender, 10000 * exp); // Mint di Paycoin per il vincitore
            emit Win_One(msg.sender, 10000 * exp); // Emette l'evento Win_One
            return true;
        } else {
            return false;
        }
    }

    // Funzione per dichiarare la vittoria in una sfida uno contro due
    function win_two(uint256 challengeIndex) public Open returns (bool) {
        require( challengeIndex < count_index, "Challenge index not valid.");
        require(!attempts[challengeIndex][msg.sender], "Attempt already made"); // NO SPAM
        attempts[challengeIndex][msg.sender] = true; // NO SPAM
        ChallengeData storage challenge = challenges[challengeIndex];
        require(challenge.winnerTwo, "Too late");
        require(msg.sender == challenge.challenger || msg.sender == challenge.rivals[0] || msg.sender == challenge.rivals[1], "Permission denied"); // Controlla se il mittente è il sfidante o uno dei rivali
        if( block.timestamp >= challenge.start + 20 seconds ){
            challenge.winnerTwo = false; // Resetta lo stato della sfida
            challenge.winner = msg.sender;
            IToken(paycoin).minting(msg.sender, 50000 * exp); // Mint di Paycoin per il vincitore
            emit Win_Two(msg.sender, 50000 * exp); // Emette l'evento Win_Two
            return true;
        } else {
            return false;
        }
    }
}