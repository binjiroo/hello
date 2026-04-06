let activeDirectoryHandle = null;

function getResultText() {
    const resultElement = document.getElementById("resultDisplay");
    return resultElement ? resultElement.innerText : "";
}

async function pickDirectory() {
    if (!window.showDirectoryPicker) {
        alert("このブラウザではフォルダ選択に対応していません。");
        return;
    }

    try {
        activeDirectoryHandle = await window.showDirectoryPicker();
        const saveButton = document.getElementById("saveInDirBtn");
        if (saveButton) {
            saveButton.disabled = false;
        }
        alert(`保存先フォルダ "${activeDirectoryHandle.name}" を選択しました。`);
    } catch (_error) {
        alert("保存先フォルダの選択をキャンセルしました。");
    }
}

async function saveInDirectory() {
    if (!activeDirectoryHandle) {
        alert("先に保存先フォルダを選択してください。");
        return;
    }

    const resultText = getResultText();
    if (!resultText) {
        alert("保存する生成結果がありません。");
        return;
    }

    const filenameElement = document.getElementById("saveFilename");
    const filename = filenameElement ? filenameElement.value : "JW_OPT4.DAT";

    try {
        const fileHandle = await activeDirectoryHandle.getFileHandle(filename, { create: true });
        const writable = await fileHandle.createWritable();
        await writable.write(resultText);
        await writable.close();
        alert(`"${filename}" を "${activeDirectoryHandle.name}" に保存しました。`);
    } catch (_error) {
        alert("ファイルの保存に失敗しました。");
    }
}

async function copyResult() {
    const resultText = getResultText();
    if (!resultText) {
        alert("コピーする生成結果がありません。");
        return;
    }

    try {
        await navigator.clipboard.writeText(resultText);
        alert("生成結果をコピーしました。");
    } catch (_error) {
        alert("生成結果のコピーに失敗しました。");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("pickDirBtn")?.addEventListener("click", pickDirectory);
    document.getElementById("saveInDirBtn")?.addEventListener("click", saveInDirectory);
    document.getElementById("copyResultBtn")?.addEventListener("click", copyResult);
});
