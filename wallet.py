import os
import zipfile
import pandas as pd
from hdwallet import HDWallet
from hdwallet.symbols import ETH as SYMBOL
from eth_account import Account
from datetime import datetime
from mnemonic import Mnemonic

# Mapping jaringan ke BIP44 coin type
NETWORKS = {
    "ethereum": 60,
    "binance_smart_chain": 60,
    "polygon": 60,
    "avalanche": 60,
    "fantom": 60,
}

# Pilih jaringan
network = "binance_smart_chain"  # Ganti dengan nama jaringan yang diinginkan

# Cek apakah jaringan didukung
if network not in NETWORKS:
    raise ValueError(f"Jaringan '{network}' tidak didukung. Pilih dari: {', '.join(NETWORKS.keys())}")

# Generate mnemonic phrase using the 'mnemonic' library
mnemo = Mnemonic("english")

# Tanyakan kepada pengguna berapa banyak wallet yang ingin dihasilkan
num_wallets = int(input("Berapa banyak wallet yang ingin dihasilkan? "))

# Inisialisasi data wallet untuk DataFrame
wallet_list = []

# Loop untuk menghasilkan beberapa wallet
for i in range(num_wallets):
    # Generate mnemonic phrase
    mnemonic = mnemo.generate(strength=128)

    # Initialize HDWallet with generated mnemonic phrase
    hdwallet = HDWallet(symbol=SYMBOL)
    coin_type = NETWORKS[network]
    hdwallet.from_mnemonic(mnemonic=mnemonic, language="english")

    # Derive key path
    try:
        hdwallet.from_path(f"m/44'/{coin_type}/0'/0/0")  # Gunakan coin type dari jaringan yang dipilih
    except Exception as e:
        print(f"Error deriving wallet: {e}")
        continue

    # Extract private key
    private_key = hdwallet.private_key()

    # Generate address from private key
    eth_account = Account.from_key(private_key)
    address = eth_account.address

    # Tambahkan data wallet ke daftar
    wallet_list.append({
        "No": i + 1,
        "Mnemonic Phrase": mnemonic,
        "Private Key": private_key,
        "Address": address,
    })

# Buat DataFrame dari data wallet
df = pd.DataFrame(wallet_list)

# Format tanggal untuk nama file
current_date = datetime.now().strftime("%d-%m-%Y")

# Format folder untuk menyimpan data
folder_name = f"wallets_{network}_{current_date}"
os.makedirs(folder_name, exist_ok=True)

# Simpan data wallet ke file teks
wallet_file_path = os.path.join(folder_name, "wallet_info.txt")
with open(wallet_file_path, "w") as file:
    file.write("+----+----------------------------------+----------------------------------------------------+----------------------------------+\n")
    file.write("| No |         Mnemonic Phrase          |                   Private Key                      |            Address                |\n")
    file.write("+----+----------------------------------+----------------------------------------------------+----------------------------------+\n")
    for index, row in df.iterrows():
        file.write(f"| {row['No']:<2} | {row['Mnemonic Phrase']:<30} | {row['Private Key']:<66} | {row['Address']:<34} |\n")
    file.write("+----+----------------------------------+----------------------------------------------------+----------------------------------+\n")

# Simpan data wallet ke file Excel
excel_file_path = os.path.join(folder_name, "wallet_info.xlsx")
df.to_excel(excel_file_path, index=False, engine='openpyxl')

# Menamai file ZIP berdasarkan jumlah wallet dan tanggal
zip_file_name = f"{num_wallets}_wallets_{current_date}.zip"

# Compress the folder into a zip file for easy download
with zipfile.ZipFile(zip_file_name, 'w') as zipf:
    zipf.write(wallet_file_path, os.path.basename(wallet_file_path))
    zipf.write(excel_file_path, os.path.basename(excel_file_path))

# Clean up by removing the folder after zipping
os.remove(wallet_file_path)
os.remove(excel_file_path)
os.rmdir(folder_name)

# Menampilkan pesan informasi setelah script dijalankan
print(f"{num_wallets} Wallets data for {network} saved as Excel and text files, compressed into {zip_file_name}. You can now download this file.")
print("#############################################")
print("#                                           #")
print("#     SC ini di buat oleh NOLIYADI         #")
print("#       Gunakan dengan bijak!               #")
print("#                                           #")
print("#############################################")
