#context:
不需要实时查询的链上数据，主要来自于缓存：chainid ，token 合约、spender 地址（来自于calldata解析）、approve 数量（来自于calldata解析）
区块数：只在查询余额，allowance时查询，作为时间戳，证明实时数据实效性。
必须来自实时查询结果（rpc等）：用户当前 allowance 和余额
其他来自于缓存数据：dApp 页面提供的说明，标记为不可信外部内容，用户本次意图

##可信事实：
来自rpc查询，calldata解析数据：chainid ，token 合约、spender 地址、approve 数量，区块数，用户当前allowance和余额。
##不可信事实：
dApp 页面提供的说明，标记为不可信外部内容，用户本次意图


