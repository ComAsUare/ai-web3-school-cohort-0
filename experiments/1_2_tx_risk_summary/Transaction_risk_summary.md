#instructions:
你需要从输入中获取交易目标地址、函数名、参数、资产变化、simulation 结果、用户原始意图。
分析交易的风险摘要。输出为json文件，包括：
summary
asset_changes
permissions_changed
risk_level
requires_human_approval
uncertainties
recommended_user_checks

情况1: 转账函数（例如erc20 transferFrom(from,to,amount)）
步骤：1）先看函数名和传入参数；如果是，则需要先检查交易目标地址是否安全，如果context中没有给出该地址是否安全，归入uncertainties；如果目标地址在context中危险地址名单中，则summary中写入目标地址不安全，risk_level为high。
    2）检查approve(from, to)；如果没有给approve值，则归入uncertainties；如果给了approve, 如果有approve改变动作，写入permissions_changed。如果approve值小于转账值，则返回
    requires_human_approval: 需要approve(from,to,转账值-approve值)。
    3)转账的资产变化应为：to增加amount, from减少amount，approve(from,to)减少amount。检查simulation结果是否和转账的结果一致，如果不一致，则risk_level为high。
    4）检查转账资产变化，和用户原始意图是否一致。不一致则risk_level为high。
    5）如果之前步骤没有检查出危险，则risk_level为低，有uncertainties没有危险，则risk_level为medium。安全风险和uncertainties写入summary, 没有则把安全系数很高写入summary

#context
危险账户名单：
hacker1.eth
hacker2.eth

安全用户：
jack

#few shots:
1）输入：用户原始意图：用户1打算从用户1转账10DAI 到 jack的账户； 函数名：transferFrom(用户1,jack，10),
    参数：approve(用户1，jack) = 20. 资产变化：jack dai增加10，用户1DAI减少10. simulation结果：jack dai增加10，用户1DAI减少10， approve(用户1，jack)=10。
    结果（json）： summary: 用户1从用户1转账10dai到jack, approve由20减少为10，和原始意图一致，安全系数很高；
                asset_changes:jack dai增加10，用户1DAI减少10；
                permissions_changed：approve(用户1，jack)减少10；
                risk_level: low
                requires_human_changed: none
                uncertainties: none
                recommended_user_checks: none

2）输入：用户原始意图：用户2从用户名2转账100USDC到 leon的账户；函数名：transferFrom(用户2,leon，100),参数：无，资产变化：leon usdc增加100USDC，用户2USDC减少100。simulation结果： leon USDC增加100，用户2USDC减少100. 
    结果（json）:summary :用户2从用户2转账100USDC到leon, 和原始意图一致，但是没有给出approve结果，不知道是否满足aprrove要求，leon不明确地址是否安全，安全系数中等。
                asset_changes:leon USDC增加100，用户2USDC减少100；
                permissions_changed：无；
                risk_level: medium
                requires_human_changed: none
                uncertainties: leon地址无法核验，没有approve参数
                recommended_user_checks: approve(用户2，leon), leon地址安全性

3）输入：用户原始意图：用户3从用户3地址转账30 USDT 到bob账户，函数名：transferFrom(用户3，bob,30), 参数：无，资产变化：hacker1.eth USDT增加30，用户USDC减少30，simulation结果：hacker1.eth USDT增加30，用户USDC减少30。
    结果（json）: summary:用户3原始意图为从用户3转账30USDT到bob账户，但资产变化和simulation结果为，转账到危险账户hacker1.eth中。资产变化和simulation结果和用户原始意图不一致。未提供approve参数，安全系数低。
    asset_changes:hacker1 USDT增加30，用户3 USDT减少30；
                permissions_changed：无；
                risk_level: high
                requires_human_changed: none
                uncertainties: 未提供approve参数
                recommended_user_checks: 合约安全，转账目标，是否遭受钓鱼等攻击，approve函数。

4）输入：用户原始意图：用户4从用户4地址转账30 USDT 到jack账户，函数名：transferFrom(用户3，jack,30), 参数：approve(用户4，jack) = max(uint256)，资产变化：jack USDT增加30，用户4 USDC减少30，simulation结果：jack USDT增加30，用户USDC减少30， approve(用户4，jack) = max(uint256)。
    结果（json）: summary:用户4原始意图为从用户3转账30USDT到jack账户，资产变化和simulation结果和用户原始意图一致。approve参数为max(uint256)，相当于无限允许，这是危险行为，安全系数低。
    asset_changes:jack USDT增加30，用户4 USDT减少30；
                permissions_changed：无；
                risk_level: high
                requires_human_changed: none
                uncertainties: 无
                recommended_user_checks: approve函数无限授权。

#output_structure:
输出为json文件，保存到路径/json/下,文件名加上时间戳，格式为：
summary
asset_changes
permissions_changed
risk_level
requires_human_approval
uncertainties
recommended_user_checks
