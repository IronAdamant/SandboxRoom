{
  Sandbox Room: read-only scan of the perk chart for the Perks & Stats room. Writes perks.tsv, one row per playable
  perk (winning version across the official masters):
    file, object ID, editor ID, name, SPECIAL (first GetBaseValue condition), required value (the chart column),
    level, number of ranks, next perk's editor ID (NNAM), sex condition (Male/Female/blank)
}
unit SBRScanPerks;

const
  OutDir = '{{OUT}}';

// The first condition calling func: its comparison value, or (param = True) its first parameter.
// (Out parameters do not come back from functions in xEdit's script engine.)
function Cond(rec: IInterface; func: string; param: boolean): string;
var
  conds, c: IInterface;
  i: integer;
begin
  Result := '';
  conds := ElementByPath(rec, 'Conditions');
  for i := 0 to ElementCount(conds) - 1 do begin
    c := ElementByPath(ElementByIndex(conds, i), 'CTDA');
    if GetElementEditValues(c, 'Function') = func then begin
      if param then
        Result := GetElementEditValues(c, 'Parameter #1')
      else
        Result := GetElementEditValues(c, 'Comparison Value');
      Exit;
    end;
  end;
end;

function Initialize: integer;
var
  i, j: integer;
  f, g, rec: IInterface;
  out, done: TStringList;
  special, column, sex: string;
begin
  out := TStringList.Create;
  for i := 0 to FileCount - 1 do begin
    f := FileByIndex(i);
    g := GroupBySignature(f, 'PERK');
    for j := 0 to ElementCount(g) - 1 do begin
      rec := ElementByIndex(g, j);
      if not IsMaster(rec) then
        Continue;
      rec := WinningOverride(rec);
      if GetElementEditValues(rec, 'DATA\Playable') <> 'True' then
        Continue;
      special := Cond(rec, 'GetBaseValue', True);
      column := Cond(rec, 'GetBaseValue', False);
      sex := Cond(rec, 'GetIsSex', True);
      out.Add(GetFileName(GetFile(MasterOrSelf(rec))) + #9 + IntToHex(FormID(rec) and $FFFFFF, 6) + #9 +
        EditorID(rec) + #9 + GetElementEditValues(rec, 'FULL') + #9 + special + #9 + column + #9 + GetElementEditValues(rec, 'DATA\Level') + #9 +
        GetElementEditValues(rec, 'DATA\Num Ranks') + #9 + EditorID(LinksTo(ElementByPath(rec, 'NNAM'))) + #9 + sex);
    end;
  end;
  out.SaveToFile(OutDir + 'perks.tsv');
  done := TStringList.Create;
  done.Add('ok');
  done.SaveToFile(OutDir + 'DONE.txt');
  done.Free;
  out.Free;
  Result := 0;
end;

end.
