<%*
const file = app.workspace.getActiveFile();
if (!file) {
  new Notice("No active file.");
  return;
}

const content = await app.vault.read(file);
const now = tp.date.now("YYYY-MM-DD HH:mm:ss") + " +0900";

let updated;

if (/^---\n[\s\S]*?\n---/.test(content)) {
  const frontmatterBlock = content.match(/^---\n[\s\S]*?\n---/)[0];

  let newFrontmatterBlock;

  if (/^last_modified_at:.*$/m.test(frontmatterBlock)) {
    newFrontmatterBlock = frontmatterBlock.replace(
      /^last_modified_at:.*$/m,
      "last_modified_at: " + now
    );
  } else {
    newFrontmatterBlock = frontmatterBlock.replace(
      /^date:.*$/m,
      match => match + "\nlast_modified_at: " + now
    );
  }

  updated = content.replace(frontmatterBlock, newFrontmatterBlock);
} else {
  updated = content;
}

await app.vault.modify(file, updated);
new Notice("last_modified_at updated: " + now);
-%>