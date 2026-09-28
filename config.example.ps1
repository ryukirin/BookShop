# 示例仅含占位符；复制到仓库外并限制访问权限，切勿在本文件写真实秘密。
# 使用 [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
# 在个人安全配置中生成全新的 32 字节随机密钥。
$env:BOOKSHOP_DATABASE_PATH = '请替换为数据库绝对路径'
$env:BOOKSHOP_UPLOAD_DIR = '请替换为上传目录绝对路径'
$env:BOOKSHOP_SECRET_KEY = '请替换为64位十六进制随机密钥'
$env:BOOKSHOP_LOG_PATH = '请替换为日志文件绝对路径'
