// Type analysis

public class EnumDescriptor extends TypeDescriptor{

   public SymbolEntry identifiers;

   public EnumDescriptor(){
      super(ENUM);
      identifiers = null;
   }

   public void setIdentifiers(SymbolEntry idList){
      identifiers = idList;
   }

   // Used in scope analysis to look up a component identifer
   public SymbolEntry findSymbol(String symbol){
      SymbolEntry entry = identifiers;
      while (entry != null){
         if (entry.name.equals(symbol))
            return entry;
         entry = entry.next;
      }
      return SymbolTable.EMPTY_SYMBOL;
   }

}