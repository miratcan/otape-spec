# Contributing to oTAPE

Thank you for helping a digital cassette feel like a real one. oTAPE is edited by **Jan Osio**, who has the
final say on what goes into the specification.

## Reporting problems

Open an issue for:

- **Ambiguities**: two careful readers could implement a rule differently.
- **Errors**: the spec, schema, geometry, templates or examples contradict each other.
- **Interoperability problems**: two implementations disagree about a real file. Attach the file, or a
  minimal one that shows the problem.

## Proposing a change

1. Open an issue describing the use case before writing spec text. Say what a person can do with a cassette
   that they can't do today.
2. Check compatibility (§15). A **minor** version may only add optional fields, values, slots or event types
   that older readers can safely ignore. Anything else needs a **major** version and a very good reason.
3. Prefer physical truth. oTAPE models a real compact cassette. Features with no physical counterpart belong in
   `extensions` (§15.3), not in the core format.
4. A pull request that changes the format updates, in one go:
   - the specification text (`oTAPE-x.y.md`), plus a line in `CHANGELOG.md`;
   - `schema/` if the manifest structure changes;
   - `geometry/` and `templates/` (run `python3 tools/make_templates.py`) if dimensions change;
   - `examples/`: at least one valid example, and an `invalid-*` example for every new rule a reader must
     enforce;
   - `tools/otape_validate.py` for every new rule.
5. Run `python3 tools/selftest.py`. CI runs it too.

## Writing style for the specification

- Use RFC 2119 keywords (MUST, SHOULD, MAY) only for requirements, always in capitals.
- Give units for every number (mm, px, frames, seconds), and put new dimensions in the geometry file.
- Say who a rule is for: reader, writer, player, recorder or editor.

## Adding an implementation

Open a pull request adding a row to the *Implementations* table in `README.md`, with a link and the conformance
class (§16) it meets. Run your files through `tools/otape_validate.py` first.

## Licence of contributions

All contributions are made under CC BY 4.0, the licence of the whole repository (see `LICENSE.md`).
