import HumbleSeedKernel.Model

/-!
# Differential-test driver

Reads scenarios on stdin, one per line:

    <variant>|<checkpoints>|<ops>

* `variant`: `v07` or `v071`
* `checkpoints`: `;`-separated `oid,seq,prevKind,prevArg,birth,body`
  where prevKind 0 = zero parent, 1 = hash of checkpoint #prevArg, 2 = junk parent
* `ops`: `;`-separated `op,index` where op 0 = record, 1 = check_current,
  2 = check_successor

Writes one line per scenario: the verdict of each op, `,`-separated. The Python
harness runs the same scenarios through the real `OwnerWitness` and compares.

The hash here only has to be injective on the checkpoints a scenario builds, so
equality patterns match the Python side's SHA-256. `diffHash` is even and ≥ 2,
the zero parent is 0 and the junk parent is 1, so the three never coincide.
-/

open HumbleSeedKernel

def cantor (a b : Nat) : Nat := (a + b) * (a + b + 1) / 2 + b

def diffHash (cp : Checkpoint) : Nat :=
  2 * cantor cp.organismId (cantor cp.sequence (cantor cp.prevHash (cantor cp.birthRoot cp.body))) + 2

def diffCrypto : Crypto where
  hashCp    := diffHash
  cpMsg     := fun _ => 0
  birthRoot := fun _ => 0
  charRoot  := fun _ => 0
  encode    := fun _ => 0
  verify    := fun _ _ _ => true
  inRange   := fun _ => true
  nextHead  := fun h => h

def junkParent : Nat := 1

def rejectName : Reject → String
  | .identityFork => "identityFork"
  | .rollback => "rollback"
  | .unwitnessedAdvance => "unwitnessedAdvance"
  | .fork => "fork"
  | .enrollmentSequence => "enrollmentSequence"
  | .enrollmentParent => "enrollmentParent"
  | .nonSuccessor => "nonSuccessor"
  | .forkedParent => "forkedParent"
  | .stateInvalid => "stateInvalid"
  | .unenrolledOrganism => "unenrolledOrganism"
  | .wrongOrganism => "wrongOrganism"

def verdictName : Verdict → String
  | .ok => "ok"
  | .reject r => rejectName r

def parseNats (s : String) : List Nat :=
  (s.splitOn ",").map String.toNat!

def prevOf (built : Array Checkpoint) (pk pa : Nat) : Nat :=
  if pk = 0 then zeroHash
  else if pk = 1 then
    (match built[pa]? with
     | some x => diffHash x
     | none => junkParent)
  else junkParent

def buildCps (specs : List (List Nat)) : Array Checkpoint := Id.run do
  let mut out : Array Checkpoint := #[]
  for sp in specs do
    let g := fun (i : Nat) => sp.getD i 0
    out := out.push ⟨g 0, g 1, prevOf out (g 2) (g 3), g 4, g 5⟩
  return out

def step (variant : String) (L : Ledger) (code : Nat) (cp : Checkpoint) : Ledger × String :=
  if code = 0 then
    let r := V07.record diffCrypto L cp
    (r.1, verdictName r.2)
  else if code = 1 then
    let v := if variant = "v071" then V071.checkCurrent diffCrypto L cp
             else V07.checkCurrent diffCrypto L cp
    (L, verdictName v)
  else
    (L, verdictName (V07.checkSuccessor diffCrypto L cp))

def runOps (variant : String) (cps : Array Checkpoint) (ops : List (List Nat)) : List String :=
  Id.run do
    let mut L : Ledger := Ledger.empty
    let mut out : Array String := #[]
    for op in ops do
      let idx := op.getD 1 0
      match cps[idx]? with
      | none => out := out.push "badindex"
      | some cp =>
        let r := step variant L (op.getD 0 0) cp
        L := r.1
        out := out.push r.2
    return out.toList

def nonEmpty (xs : List String) : List String := xs.filter (fun x => !x.isEmpty)

def processLine (line : String) : String :=
  match line.splitOn "|" with
  | [variant, cpsStr, opsStr] =>
    let specs := (nonEmpty (cpsStr.splitOn ";")).map parseNats
    let ops := (nonEmpty (opsStr.splitOn ";")).map parseNats
    String.intercalate "," (runOps variant (buildCps specs) ops)
  | _ => "badline"

partial def loop (stdin stdout : IO.FS.Stream) : IO Unit := do
  let line ← stdin.getLine
  if line.isEmpty then
    return
  let t := line.trimRight
  if !t.isEmpty then
    stdout.putStrLn (processLine t)
  loop stdin stdout

def main : IO Unit := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  loop stdin stdout
