const hre = require('hardhat');

module.exports = async ({ deployments }) => {
  const verifiedContract = await deployments.get('verifiedContract');
  await hre.run('verify:verify', {
    address: '',
    constructorArguments: [],
  });
};
module.exports.tags = ['verify'];
