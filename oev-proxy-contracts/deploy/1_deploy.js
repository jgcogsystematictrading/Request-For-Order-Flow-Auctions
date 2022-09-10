const hre = require('hardhat');

module.exports = async ({ getUnnamedAccounts, deployments }) => {
  const { deploy, log } = deployments;
  const accounts = await getUnnamedAccounts();

  const ContractToDeploy = await deploy('ContractToDeploy', {
    from: accounts[0],
    log: true,
    deterministicDeployment: process.env.DETERMINISTIC ? hre.ethers.constants.HashZero : undefined,
  });
  log(`Deployed <ContractToDeploy> at ${accessControlRegistry.address}`);
};
module.exports.tags = ['deploy'];
