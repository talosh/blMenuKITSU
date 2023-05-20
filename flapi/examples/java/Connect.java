import uk.ltd.filmlight.flapi.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

class Connect {

    public static void main( String[] args )
    {
        Connection conn = null;
        String host = "localhost";

        for( int i = 0; i < args.length; ++i )
        {
            if( args[i].equals("-h") )
            {
                if( i < (args.length-1) )
                {
                    host = args[++i];
                }
                else
                {
                    System.out.printf( "No hostname specified for -h argument\n" );
                    System.exit(1);
                }
            }
        }

        try
        {
            conn = new Connection(host);
            conn.connect();
            System.out.printf( "Connection to FLAPI server %s OK\n", host );
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
