import os
import zipfile
import datetime
import pandas as pd
from hdwallet import HDWallet
from hdwallet.symbols import ETH
from hdwallet.utils import generate_mnemonic
from mnemonic import Mnemonic  # Library tambahan untuk Sui, Solana, Aptos
from aptos_sdk.account import Account  # SDK Aptos
from bip_utils import Bip39SeedGenerator, Bip44Coins, Bip44
from bech32 import bech32_encode, convertbits
from typing import List

# Daftar jaringan yang didukung dan coin types sesuai standar BIP44
NETWORKS = {
    "1": ("Ethereum", ETH, "🌍"),
    "2": ("Binance Smart Chain", ETH, "🔶"),  # Gunakan ETH untuk BSC sebagai EVM-based
    "3": ("Polygon", ETH, "🔺"),
    "4": ("Avalanche", ETH, "❄️"),
    "5": ("Fantom", ETH, "👻"),
    "6": ("Sui", "sui", "🐢"),
    "7": ("Aptos", "aptos", "🐎")
}

class SuiWallet:
    def __init__(self, mnemonic: str, password='') -> None:
        self.mnemonic: str = mnemonic.strip()
        self.password = password
        self.pk_prefix = 'suiprivkey'
        self.ed25519_schema = '00'

    def get_address_pk(self, pk_with_prefix=True):
        seed_bytes = Bip39SeedGenerator(self.mnemonic).Generate(self.password)
        bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.SUI).DeriveDefaultPath()
        address = bip44_mst_ctx.PublicKey().ToAddress()
        pk = bip44_mst_ctx.PrivateKey().Raw().ToHex()

        if pk_with_prefix:
            pk_bytes_with_schema = bytes.fromhex(f'{self.ed25519_schema}{pk}')
            pk_bit_arr = convertbits(pk_bytes_with_schema, 8, 5)
            pk = bech32_encode(self.pk_prefix, pk_bit_arr)

        return address, pk

def create_wallet(network_symbol):
    """Membuat wallet untuk jaringan yang dipilih."""
    if network_symbol == ETH:
        hdwallet = HDWallet(symbol=network_symbol)
        mnemonic = generate_mnemonic()
        hdwallet.from_mnemonic(mnemonic)
        address = hdwallet.p2pkh_address()
        private_key = hdwallet.private_key()

    elif network_symbol == "sui":
        mnemonic = generate_mnemonic()
        sui_wallet = SuiWallet(mnemonic)
        address, private_key = sui_wallet.get_address_pk()

    elif network_symbol == "aptos":
        mnemonic = generate_mnemonic()
        account = Account.generate()
        address = str(account.address())  # Konversikan langsung ke string
        private_key = account.private_key.hex()

    return mnemonic, private_key, address

def main():
    # Tampilan pengantar
    print("════════════════════════════════════════════════════════════")
    print("    🌐 Wallet Generator - Script oleh NOLIYADI 🌐")
    print("════════════════════════════════════════════════════════════")
    print("\n📜 Script ini mendukung pembuatan wallet untuk jaringan:\n")

    # Tampilkan daftar jaringan
    for key, (network, _, icon) in NETWORKS.items():
        print(f"🚩 {key}) {network} {icon}")

    print("\n------------------------------------------------------------")
    print("⚙️ *Langkah-langkah pembuatan wallet:*")
    print("  1️⃣ Pilih nomor jaringan (atau beberapa jaringan dengan koma)")
    print("     ➡️ Contoh: 1,3,6")
    print("  2️⃣ Masukkan jumlah wallet yang ingin Anda buat untuk setiap jaringan")
    print("\n------------------------------------------------------------")

    # Input jaringan yang ingin digunakan
    network_choice = input("🔸 Masukkan nomor jaringan pilihan Anda: ").split(',')
    network_choice = [x.strip() for x in network_choice if x.strip() in NETWORKS]

    # Validasi pilihan jaringan
    if not network_choice:
        print("❌ Pilihan jaringan tidak valid. Harap coba lagi.")
        return

    # Input jumlah wallet yang diinginkan
    wallet_count = int(input("🔹 Masukkan jumlah wallet yang ingin Anda buat: "))

    # Inisialisasi data wallet
    wallet_data = []

    print("\n🔄 Proses pembuatan wallet sedang berlangsung...\n")

    # Pembuatan wallet untuk setiap jaringan yang dipilih
    for choice in network_choice:
        network_name, network_symbol, icon = NETWORKS[choice]
        print(f"   ➔ {network_name} {icon}")
        
        for i in range(wallet_count):
            mnemonic, private_key, address = create_wallet(network_symbol)
            wallet_data.append({
                "No": i + 1,
                "Network": network_name,
                "Mnemonic Phrase": mnemonic,
                "Private Key": private_key,
                "Address": address
            })

    # Buat DataFrame dan simpan sebagai file Excel
    df = pd.DataFrame(wallet_data)
    today = datetime.date.today().strftime("%d-%m-%Y")
    filename = f"{wallet_count}_wallets_{today}.xlsx"
    df.to_excel(filename, index=False)

    # Kompres file Excel ke dalam ZIP
    zip_filename = f"{wallet_count}_wallets_{today}.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(filename)
    os.remove(filename)

    print("\n════════════════════════════════════════════════════════════")
    print(f"🎉 {wallet_count} Wallets berhasil dihasilkan!")
    print(f"💾 Data disimpan sebagai: {zip_filename}")
    print("\n════════════════════════════════════════════════════════════")
    print("⚠️  SC ini di buat oleh NOLIYADI. Gunakan dengan bijak! ⚠️")
    print("════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    main()
