{
  Sandbox Room: read-only scan of the official masters. Writes tab-separated lists the build tools pick from:
    items.tsv     every item record (WEAP ARMO AMMO ALCH MISC BOOK) with name, flags and keywords
    world.tsv     FURN, STAT, TERM, LVLN, LGTM, CONT, MSTT, LIGH, DOOR, ACTI records with name, bounds and model
    cells.tsv     interior cells with their flags and lighting template
    omods.tsv     object mods (OMOD) with name, form type (Weapon/Armor) and description
}
unit SBRScan;

const
  OutDir = '{{OUT}}';

var
  items, world, cells, omods: TStringList;

function Clean(s: string): string;
begin
  Result := StringReplace(StringReplace(s, #9, ' ', [rfReplaceAll]), #13#10, ' ', [rfReplaceAll]);
end;

function Keywords(rec: IInterface): string;
var
  kw: IInterface;
  i: integer;
begin
  Result := '';
  kw := ElementByPath(rec, 'KWDA');
  for i := 0 to ElementCount(kw) - 1 do
    Result := Result + EditorID(LinksTo(ElementByIndex(kw, i))) + ',';
end;

function ObjBounds(rec: IInterface): string;
begin
  Result := GetElementEditValues(rec, 'OBND\X1') + ',' + GetElementEditValues(rec, 'OBND\Y1') + ',' +
    GetElementEditValues(rec, 'OBND\Z1') + ',' + GetElementEditValues(rec, 'OBND\X2') + ',' +
    GetElementEditValues(rec, 'OBND\Y2') + ',' + GetElementEditValues(rec, 'OBND\Z2');
end;

procedure ScanGroup(f, g: IInterface);
var
  i: integer;
  rec: IInterface;
  sig, line: string;
begin
  for i := 0 to ElementCount(g) - 1 do begin
    rec := ElementByIndex(g, i);
    if Signature(rec) = 'GRUP' then begin
      // interior cell blocks and sub-blocks only; never the reference groups under each cell
      if (GroupType(rec) = 2) or (GroupType(rec) = 3) then
        ScanGroup(f, rec);
      Continue;
    end;
    if not IsMaster(rec) then
      Continue;
    sig := Signature(rec);
    line := GetFileName(f) + #9 + IntToHex(FormID(rec), 8) + #9 + sig + #9 + EditorID(rec) + #9 +
      Clean(GetElementEditValues(rec, 'FULL'));
    if (sig = 'WEAP') or (sig = 'ARMO') or (sig = 'AMMO') or (sig = 'ALCH') or (sig = 'MISC') or (sig = 'BOOK') then
      items.Add(line + #9 + IntToHex(GetElementNativeValues(rec, 'Record Header\Record Flags'), 8) + #9 +
        GetElementEditValues(rec, 'DATA\Flags') + #9 + GetElementEditValues(rec, 'DNAM\Flags') + #9 +
        GetElementEditValues(rec, 'Model\MODL') + #9 + Keywords(rec) + #9 +
        IntToStr(ElementCount(ElementByPath(rec, 'CVPA'))) + #9 + GetElementEditValues(rec, 'BOD2\First Person Flags') + #9 +
        GetElementEditValues(rec, 'DATA\Value'))
    else if (sig = 'FURN') or (sig = 'STAT') or (sig = 'TERM') or (sig = 'LVLN') or (sig = 'LGTM') or (sig = 'CONT')
      or (sig = 'MSTT') or (sig = 'LIGH') or (sig = 'DOOR') or (sig = 'ACTI') then
      world.Add(line + #9 + ObjBounds(rec) + #9 + GetElementEditValues(rec, 'Model\MODL') + #9 + Keywords(rec))
    else if sig = 'OMOD' then
      omods.Add(line + #9 + GetElementEditValues(rec, 'DATA\Form Type') + #9 + Clean(GetElementEditValues(rec, 'DESC')))
    else if sig = 'CELL' then
      cells.Add(line + #9 + GetElementEditValues(rec, 'DATA') + #9 + GetElementEditValues(rec, 'LTMP') + #9 +
        GetElementEditValues(rec, 'XCIM') + #9 + GetElementEditValues(rec, 'XCCM') + #9 +
        GetElementEditValues(rec, 'XLCN'));
  end;
end;

function Initialize: integer;
var
  i, j: integer;
  f, g: IInterface;
  sig: string;
  done, progress: TStringList;
begin
  progress := TStringList.Create;
  items := TStringList.Create;
  world := TStringList.Create;
  cells := TStringList.Create;
  omods := TStringList.Create;
  for i := 0 to FileCount - 1 do begin
    f := FileByIndex(i);
    if (Pos('.esm', LowerCase(GetFileName(f))) = 0) then
      Continue;
    for j := 0 to ElementCount(f) - 1 do begin
      g := ElementByIndex(f, j);
      if Signature(g) <> 'GRUP' then
        Continue;
      // top group type = signature of its first record; the cell group starts with block sub-groups
      if ElementCount(g) = 0 then
        Continue;
      sig := Signature(ElementByIndex(g, 0));
      if (sig = 'GRUP') and (Pos('CELL', Name(g)) > 0) then
        sig := 'CELL';
      if (sig = 'WEAP') or (sig = 'ARMO') or (sig = 'AMMO') or (sig = 'ALCH') or (sig = 'MISC') or (sig = 'BOOK')
        or (sig = 'FURN') or (sig = 'STAT') or (sig = 'TERM') or (sig = 'LVLN') or (sig = 'LGTM') or (sig = 'CONT')
        or (sig = 'MSTT') or (sig = 'LIGH') or (sig = 'DOOR') or (sig = 'ACTI') or (sig = 'CELL') or (sig = 'OMOD') then
      begin
        ScanGroup(f, g);
        progress.Add(GetFileName(f) + ' ' + sig);
        progress.SaveToFile(OutDir + 'progress.txt');
      end;
    end;
  end;
  items.SaveToFile(OutDir + 'items.tsv');
  world.SaveToFile(OutDir + 'world.tsv');
  cells.SaveToFile(OutDir + 'cells.tsv');
  omods.SaveToFile(OutDir + 'omods.tsv');
  done := TStringList.Create;
  done.Add('ok');
  done.SaveToFile(OutDir + 'DONE.txt');
  done.Free;
  Result := 0;
end;

end.
