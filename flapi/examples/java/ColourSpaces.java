import uk.ltd.filmlight.flapi.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

class ColourSpaces {

    public static void main( String[] args )
    {
        Connection conn = null;

        try
        {
            conn = new Connection("localhost");
            conn.launch();

            FormatSet globalFormats = conn.FormatSet.factoryFormats();

            ArrayList<String> csNames = globalFormats.getColourSpaceNames();

            System.out.printf( "Found %d colour spaces\n", csNames.size() );
            for( String n : csNames )
                System.out.printf( "    %s\n", n );

            conn.close();
        }
        catch( FLAPIException ex )
        {
            System.out.printf( "Error: %s\n", ex.getMessage() );
            System.exit(1);
        }
        finally
        {
            if( conn != null )
                conn.close();
        }
    }
}
