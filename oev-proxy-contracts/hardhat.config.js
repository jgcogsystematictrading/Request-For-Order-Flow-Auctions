require('@nomiclabs/hardhat-waffle');
require('@nomiclabs/hardhat-etherscan');
require('solidity-coverage');
require('hardhat-gas-reporter');
require('hardhat-deploy');

const fs = require('fs');
let credentials = require('./credentials.example.json');
if (fs.existsSync('./credentials.json')) {
    credentials = require('./credentials.json');
}

module.exports = {
    etherscan: credentials.etherscan,
    gasReporter: {
        enabled: process.env.REPORT_GAS ? true : false,
        outputFile: 'gas_report',
        noColors: true,
    },
    mocha: {
        timeout: process.env.EXTENDED_TEST ? 3600000 : 20000,
    },
    networks: credentials.networks,
    paths: {
        tests: process.env.EXTENDED_TEST ? './extended-test' : './test',
    },
    solidity: {
        version: '0.8.14',
        settings: {
            optimizer: {
                enabled: true,
                runs: 1000,
            },
        },
    },
};
