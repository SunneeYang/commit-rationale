---
name: commit-rationale
description: Write Git commit messages that preserve useful rationale and context not recoverable from code or diff. Use when preparing a commit, drafting or improving its message, or preserving context during an authorized amend, squash, or merge. Do not use for code review or impact analysis alone.
---

# Commit Rationale

Write an ordinary commit subject. Add a body only for supported information that
future maintainers may need and cannot reliably recover from the code and diff.
A subject-only message is a complete, valid result.

## Establish the change and its context

- Read repository instructions and recent commit messages for language and style.
  Follow the user's preference; do not impose Conventional Commits on a repository
  that does not use them.
- Check the repository, branch, working tree, index, and intended commit scope.
  Read the actual diff to be committed and enough surrounding code to understand
  it. Keep staged, unstaged, and unrelated changes distinct. For a message-only
  request, inspect the supplied or requested diff without changing the index.
- Use relevant task conversation, user requirements, recorded decisions, actual
  verification results, and available durable references. Read linked material
  only as needed to establish a fact; do not search unrelated private history.
- Separate observed behavior from historical intent. A plausible explanation
  inferred from a diff is not evidence of why the author made the change. When a
  human wrote the code and the agent only prepares the commit, do not invent a
  development narrative or imply agent authorship. User-supplied rationale can
  still be valuable in that case.

## Keep only information worth preserving

For each possible body detail, ask: **Is it supported, useful for maintaining this
change, and difficult to recover from code and diff?** Keep it only if all three
conditions hold. Useful examples include:

- External business, client, compatibility, or operational constraints.
- Why a non-obvious choice was made, including a rejected alternative when its
  rejection explains a lasting tradeoff.
- An intentional limitation, temporary workaround, or condition for removing it.
- Material verification evidence or gaps: what was actually checked, its outcome,
  and a relevant limitation. Distinguish a user-reported result from a result you
  observed; never turn a planned check into a passed check.

Omit file inventories, implementation walkthroughs, diff paraphrases, routine
progress logs, speculative impact/risk labels, and empty statements such as
"No special decisions." Do not copy raw chats, internal reasoning transcripts,
credentials, or private operational details into permanent Git history. Preserve
the necessary engineering fact in a concise, shareable form.

Missing rationale is not a blocker by itself. Omit unsupported claims rather than
asking the user to explain every ordinary change. Ask a focused question only
when a material ambiguity prevents an accurate message or a safe requested commit.

## Compose the message

- **Subject:** Describe the final change concisely in the repository's style.
- **Body:** Use the shortest natural-language explanation that preserves the
  relevant facts. Leave one blank line after the subject. There is no required
  schema, section order, or minimum length. Use paragraphs or bullets as useful;
  do not require `Intent`, `Constraints`, `Decision`, or `Verification` headings.
- **Trailers:** Optional. Use stable, known external references such as `Task-Ref`
  or `ADR-Ref` when useful and consistent with repository conventions. Preserve
  standard trailers with their actual meaning; never invent IDs, sign-offs,
  co-authorship, reviews, or test attestations. Put trailers in the final block,
  separated from the body by a blank line, and use Git's native trailer support.

Do not add `Agent`, `Agent-Context-Version`, model/session identifiers, or
"prepared by" provenance by default. Executing `git commit` does not establish
who authored the code. Follow an explicit user or repository metadata requirement
without guessing unknown values. Do not introduce a parser, schema, or hook to
enforce a body format.

For amend, squash, or merge messages, inspect the relevant original messages and
the final combined change. Preserve still-relevant constraints and rationale;
remove superseded claims, duplicated explanations, and intermediate chronology.
Do not present tests on an earlier tree as validation of the final tree. Preserve
applicable references and standard attestations without broadening their scope.

## Deliver within the requested scope

A request for a message authorizes a draft, not a commit. An already-authorized
commit does not require another approval just because this skill is active.
The skill itself grants no permission to stage unrelated files, amend history,
merge branches, push, publish, or change Git configuration.

When committing is requested, follow repository Git instructions, stage only the
authorized files or hunks, and recheck the final staged diff against the message.
Write multiline text to a temporary UTF-8 file and use `git commit -F` with that
file; use `--trailer` for any needed trailers without duplicating existing ones.
Keep the temporary file outside the tracked change, avoid shell interpolation
of message text, and remove it afterward. Respect hooks and signing requirements.
After success, inspect the resulting commit message and diff, then report its ID
and any remaining changes. Report failures accurately; do not bypass a failed
hook or retry a potentially completed commit blindly. Push only when authorized.

For a draft, return the message directly. Do not append an explanation of why the
body is empty unless the user asks.

## Examples

Human changed a timeout from three to five seconds; no rationale was supplied:

```text
fix(gateway): increase request timeout
```

The task explicitly established an upstream delay and a client deadline:

```text
fix(gateway): increase request timeout

The upstream payment service can take 3–4 seconds during daily settlement.
Five seconds is the client deadline, so the timeout must not increase further.
```

An established compatibility constraint and a known task reference:

```text
fix(auth): preserve the legacy expired-token response

Clients before 3.12 interpret the new error code as a transport failure.
Keep the old response until those client versions are retired.

Task-Ref: GAME-1832
```

These facts and identifiers illustrate the format; never copy them into an
unrelated commit. Adapt the wording and language to the actual evidence.
