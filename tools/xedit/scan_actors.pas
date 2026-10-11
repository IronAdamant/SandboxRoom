{
  Sandbox Room: read-only scan of Fallout4.esm for the target range's custom targets. Writes:
    efsh.tsv      effect shaders (EFSH) with their fill/edge colours and textures, to pick a hologram look
    npcs.tsv      actors (NPC_) with name, race, template, template flags and level
}
unit SBRScanActors;

const
  OutDir = '{{OUT}}';

function Clean(s: string): string;
begin
  Result := StringReplace(StringReplace(s, #9, ' ', [rfReplaceAll]), #13#10, ' ', [rfReplaceAll]);
end;

function Initialize: integer;
var
  i, j: integer;
  f, g, rec: IInterface;
  efsh, npcs, done: TStringList;
begin
  efsh := TStringList.Create;
  npcs := TStringList.Create;
  for i := 0 to FileCount - 1 do begin
    f := FileByIndex(i);
    if not SameText(GetFileName(f), 'Fallout4.esm') then
      Continue;
    g := GroupBySignature(f, 'EFSH');
    for j := 0 to ElementCount(g) - 1 do begin
      rec := ElementByIndex(g, j);
      efsh.Add(IntToHex(FormID(rec), 8) + #9 + EditorID(rec) + #9 + Clean(GetElementEditValues(rec, 'ICON')) + #9 +
        Clean(GetElementEditValues(rec, 'ICO2')) + #9 + Clean(GetElementEditValues(rec, 'NAM7')) + #9 +
        Clean(GetElementEditValues(rec, 'NAM8')) + #9 + Clean(GetElementEditValues(rec, 'NAM9')));
    end;
    g := GroupBySignature(f, 'NPC_');
    for j := 0 to ElementCount(g) - 1 do begin
      rec := ElementByIndex(g, j);
      npcs.Add(IntToHex(FormID(rec), 8) + #9 + EditorID(rec) + #9 + Clean(GetElementEditValues(rec, 'FULL')) + #9 +
        GetElementEditValues(rec, 'RNAM') + #9 + GetElementEditValues(rec, 'TPLT') + #9 +
        GetElementEditValues(rec, 'ACBS\Template Flags') + #9 + GetElementEditValues(rec, 'ACBS\Level'));
    end;
  end;
  efsh.SaveToFile(OutDir + 'efsh.tsv');
  npcs.SaveToFile(OutDir + 'npcs.tsv');
  done := TStringList.Create;
  done.Add('ok');
  done.SaveToFile(OutDir + 'DONE.txt');
  Result := 0;
end;

end.
