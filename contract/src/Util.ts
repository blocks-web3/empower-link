import { Contract, Signer, Wallet } from "ethers";
import hre, { ethers } from "hardhat";

export type MultisigWallet = {
  signer: Signer;
  walletContract: Contract;
};

export async function createWallet(
  factory: Contract,
  salt: number,
  bundlerSigner: Signer,
  ownerSigner?: Signer
): Promise<MultisigWallet> {
  const signer = ownerSigner || getAccount();
  const walletAddress = await factory.getAddress(
    await signer.getAddress(),
    salt
  );

  const artifact = await hre.deployments.getArtifact("SimpleAccount");
  const walletContract = new ethers.Contract(
    walletAddress,
    artifact.abi,
    bundlerSigner
  );

  if (!(await existsAddress(walletAddress))) {
    const res = await factory.createAccount(await signer.getAddress(), salt);
    console.debug("==account created!! tx=", res.hash);
  }
  return { signer, walletContract };
}

export async function existsAddress(address: string): Promise<boolean> {
  const code = await ethers.provider.getCode(address);
  return code !== "0x";
}

export function getAccount(): Wallet {
  return ethers.Wallet.createRandom();
}

export async function getEtherBalance(address: string): Promise<string> {
  const balance = await ethers.provider.getBalance(address);
  return ethers.utils.formatEther(balance);
}
